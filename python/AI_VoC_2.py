# coding=gbk

import os
import json
import pickle
import re
import math
import numpy as np
import pandas as pd
from collections import defaultdict
from openai import OpenAI
from sklearn.cluster import KMeans

# =========================
# Config
# =========================
API_KEY = os.getenv("OPENAI_API_KEY", "xxx")

MODEL_TEXT = "gpt-5.1"
EMBED_MODEL = "text-embedding-3-large"

INPUT_MANUAL = "correct_manual_record_202405.json"
INPUT_TICKETS = "TicketsCard_202405.json"
EMBED_CACHE_FILE = "embeddings_scheme_b_cache.pickle"

OUTPUT_CLUSTER_CSV = "ai_output1_scheme_b.csv"
OUTPUT_ISSUE_CSV = "ai_output2_scheme_b.csv"

MAX_TICKETS = 100
MAX_TEXT_LEN = 8000

# 主聚类上限
MAX_MAIN_K = 8

# 仅对大簇继续细分
MIN_CLUSTER_SIZE_FOR_SPLIT = 8

# 小于这个就不做簇总结
MIN_CLUSTER_SIZE_FOR_SUMMARY = 3

# 若簇内平均余弦相似度已经很高，则不再细分
SIMILARITY_SPLIT_THRESHOLD = 0.82

# 二级细分最大簇数
MAX_SUB_K = 4

client = OpenAI(api_key=API_KEY)

# =========================
# Basic Helpers
# =========================
def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def safe_get(d, key, default=""):
    return d[key] if key in d and d[key] is not None else default


def normalize_rows(x):
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1e-12
    return x / norms


def cosine_similarity_matrix(x):
    x_norm = normalize_rows(x)
    return x_norm @ x_norm.T


def average_pairwise_cosine(x):
    if len(x) <= 1:
        return 1.0
    sim = cosine_similarity_matrix(x)
    n = sim.shape[0]
    mask = ~np.eye(n, dtype=bool)
    vals = sim[mask]
    if len(vals) == 0:
        return 1.0
    return float(np.mean(vals))


def call_text_model(prompt, verbosity="low"):
    response = client.responses.create(
        model=MODEL_TEXT,
        input=prompt,
        reasoning={"effort": "low"},
        text={"verbosity": verbosity},
    )
    return response.output_text.strip()


def get_embedding(text):
    text = clean_text(text)[:MAX_TEXT_LEN]
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=[text]
    )
    return response.data[0].embedding


def summarize_ticket(text):
    prompt = f"""
Please summarize the following support ticket in 2-4 concise sentences.
Focus on:
1. the user's problem,
2. impacted function or service,
3. likely issue category.

Ticket text:
{text[:MAX_TEXT_LEN]}
"""
    return call_text_model(prompt, verbosity="low")


def build_ticket_description(ticket, reference_ans, use_reference_prefix=False):
    """
    默认不把人工答案拼进文本，避免数据污染。
    如果你明确要半监督，可以改 use_reference_prefix=True
    """
    ticket_id = safe_get(ticket, "Ticket ID", "")
    subject = clean_text(safe_get(ticket, "Subject", ""))
    description = clean_text(safe_get(ticket, "Description", ""))

    full_text = f"{subject}\t{description}"

    if use_reference_prefix and ticket_id in reference_ans:
        key_issue, issue_summary = reference_ans[ticket_id]
        full_text = f"This is about {key_issue}-{issue_summary}; {full_text}"

    return full_text


# =========================
# Clustering Helpers
# =========================
def determine_optimal_clusters(data, max_k=8):
    n_samples = len(data)
    if n_samples <= 1:
        return 1
    if n_samples == 2:
        return 2

    max_k = min(max_k, n_samples)
    inertias = []

    for k in range(1, max_k + 1):
        km = KMeans(n_clusters=k, random_state=42, n_init="auto")
        km.fit(data)
        inertias.append(km.inertia_)

    if len(inertias) < 3:
        return min(2, n_samples)

    diffs = np.diff(inertias)
    diff_in_diff = np.diff(diffs)

    if len(diff_in_diff) == 0:
        return min(2, n_samples)

    optimal_k = int(np.argmax(diff_in_diff) + 2)
    return max(1, min(optimal_k, n_samples))


def should_split_cluster(cluster_embeddings, min_size=MIN_CLUSTER_SIZE_FOR_SPLIT,
                         similarity_threshold=SIMILARITY_SPLIT_THRESHOLD):
    """
    只对“大且不够紧”的簇继续拆
    """
    if len(cluster_embeddings) < min_size:
        return False

    avg_sim = average_pairwise_cosine(cluster_embeddings)
    if avg_sim >= similarity_threshold:
        return False

    return True


def split_large_cluster(cluster_embeddings, max_sub_k=MAX_SUB_K):
    """
    对大簇做一次细分
    """
    n = len(cluster_embeddings)
    if n <= 2:
        return np.zeros(n, dtype=int)

    optimal_sub_k = determine_optimal_clusters(cluster_embeddings, max_k=min(max_sub_k, n))
    if optimal_sub_k <= 1:
        return np.zeros(n, dtype=int)

    km = KMeans(n_clusters=optimal_sub_k, random_state=42, n_init="auto")
    labels = km.fit_predict(cluster_embeddings)
    return labels


# =========================
# Parsing Helpers
# =========================
def parse_cluster_summary(raw_text):
    cleaned = raw_text.replace("*", "").replace("#", "").strip()

    ticket_pattern = re.compile(
        r"Ticket\s*Id:\s*(.*?)\s*"
        r"Ticket\s*Label:\s*(.*?)\s*"
        r"Ticket\s*Summary:\s*(.*?)(?=(?:\n\s*Ticket\s*Id:)|(?:\n\s*Overall\s*Label:)|$)",
        re.IGNORECASE | re.DOTALL
    )

    ticket_matches = ticket_pattern.findall(cleaned)

    overall_label = ""
    overall_summary = ""

    m1 = re.search(r"Overall\s*Label:\s*(.*)", cleaned, re.IGNORECASE)
    if m1:
        overall_label = clean_text(m1.group(1))

    m2 = re.search(r"Overall\s*Summary:\s*(.*)", cleaned, re.IGNORECASE)
    if m2:
        overall_summary = clean_text(m2.group(1))

    parsed_ticket_items = []
    for t_id, t_label, t_summary in ticket_matches:
        parsed_ticket_items.append((
            clean_text(t_id),
            clean_text(t_label),
            clean_text(t_summary),
        ))

    return parsed_ticket_items, overall_label, overall_summary


def parse_issue_output(raw_text):
    blocks = [b.strip() for b in raw_text.split("===") if b.strip()]
    rows = []

    for block in blocks:
        key_issue = ""
        issue_summary = ""
        related_tickets = ""

        m1 = re.search(r"Key\s*Issue:\s*(.*)", block, re.IGNORECASE)
        if m1:
            key_issue = clean_text(m1.group(1))

        m2 = re.search(r"Issue\s*Summary:\s*(.*)", block, re.IGNORECASE)
        if m2:
            issue_summary = clean_text(m2.group(1))

        m3 = re.search(r"Related\s*Tickets:\s*(.*)", block, re.IGNORECASE)
        if m3:
            related_tickets = clean_text(m3.group(1))

        if key_issue or issue_summary or related_tickets:
            rows.append({
                "Key Issue": key_issue,
                "Issue Summary": issue_summary,
                "Ticket List": related_tickets
            })

    return rows


# =========================
# Step 1: Load manual references
# =========================
reference_ans = {}
if os.path.exists(INPUT_MANUAL):
    with open(INPUT_MANUAL, "r", encoding="utf-8") as f:
        raw = json.load(f)
        for item in raw:
            ticket_id = safe_get(item, "Ticket ID", "")
            key_issue = safe_get(item, "Key Issue", "")
            issue_summary = safe_get(item, "Issue Summary", "")
            reference_ans[ticket_id] = [key_issue, issue_summary]

# =========================
# Step 2: Load tickets
# =========================
tickets = []
with open(INPUT_TICKETS, "r", encoding="utf-8") as f:
    ticket_info = json.load(f)

for ticket in ticket_info[:MAX_TICKETS]:
    ticket_id = safe_get(ticket, "Ticket ID", "")
    description = build_ticket_description(ticket, reference_ans, use_reference_prefix=False)
    tickets.append((ticket_id, description))

# =========================
# Step 3: Load / create embeddings cache
# =========================
embeddings_map = {}
if os.path.exists(EMBED_CACHE_FILE):
    try:
        with open(EMBED_CACHE_FILE, "rb") as f:
            embeddings_map = pickle.load(f)
        print(f"loaded embeddings from {EMBED_CACHE_FILE}")
    except Exception as e:
        print(f"failed to load cache: {e}")
        embeddings_map = {}

for ticket_id, description in tickets:
    if ticket_id in embeddings_map:
        continue

    print(f"processing ticket: {ticket_id}")

    try:
        description_embedding = get_embedding(description)
        description_summary = summarize_ticket(description)
    except Exception as e:
        print(f"error fetching {ticket_id}: {e}")
        continue

    embeddings_map[ticket_id] = (
        ticket_id,
        description_embedding,
        description_summary,
        description
    )

    with open(EMBED_CACHE_FILE, "wb") as f:
        pickle.dump(embeddings_map, f, protocol=pickle.HIGHEST_PROTOCOL)

# =========================
# Step 4: Prepare embeddings
# =========================
items = [embeddings_map[k] for k in embeddings_map]
if not items:
    raise RuntimeError("No tickets processed. Check input files and API key.")

embeddings = np.array([np.array(item[1]) for item in items])

# =========================
# Step 5: Main clustering
# =========================
main_k = determine_optimal_clusters(embeddings, max_k=MAX_MAIN_K)
main_clusterer = KMeans(n_clusters=main_k, random_state=42, n_init="auto")
main_labels = main_clusterer.fit_predict(embeddings)

# =========================
# Step 6: Split only large / loose clusters
# =========================
final_labels = []

for main_label in np.unique(main_labels):
    idxs = np.where(main_labels == main_label)[0]
    cluster_embs = embeddings[idxs]

    if should_split_cluster(cluster_embs):
        sub_labels = split_large_cluster(cluster_embs)

        # 如果细分结果全一样，也视作不拆
        if len(np.unique(sub_labels)) <= 1:
            for local_idx in idxs:
                final_labels.append((local_idx, (int(main_label), 0)))
        else:
            for pos, local_idx in enumerate(idxs):
                final_labels.append((local_idx, (int(main_label), int(sub_labels[pos]))))
    else:
        for local_idx in idxs:
            final_labels.append((local_idx, (int(main_label), 0)))

# 按原顺序还原
final_labels = sorted(final_labels, key=lambda x: x[0])
compound_labels = [label for _, label in final_labels]

# =========================
# Step 7: Build cluster map
# =========================
cluster_map = defaultdict(list)
ticket_cluster_map = {}

for i, label_tuple in enumerate(compound_labels):
    label_str = f"{label_tuple[0]}-{label_tuple[1]}"
    ticket_id, embedding_vec, ticket_summary, ticket_text = items[i]

    ticket_cluster_map[ticket_id] = label_tuple
    cluster_map[label_str].append((ticket_id, label_str, ticket_summary, ticket_text))

sorted_clusters = sorted(cluster_map.values(), key=lambda x: len(x), reverse=True)

print(ticket_cluster_map)

# =========================
# Step 8: Summarize each cluster
# =========================
summary_rows = []
ticket_sum_list = []

total_clustered_tickets = sum(len(c) for c in sorted_clusters)

for cluster in sorted_clusters:
    if len(cluster) < MIN_CLUSTER_SIZE_FOR_SUMMARY:
        print(">> Too short, skip cluster summary")
        continue

    docs = []
    for ticket_id, label, ticket_summary, ticket_text in cluster:
        docs.append(
            f"Ticket Id: {ticket_id}\n"
            f"Ticket Summary Input: {ticket_summary}"
        )

    combined_docs = "\n----------------\n".join(docs)

    prompt = f"""
Each document is separated by "----------------".

Task 1:
For each document, output exactly:
Ticket Id: xxxx
Ticket Label: xxxx
Ticket Summary: xxxx

Task 2:
Then output exactly:
Overall Label: xxxx
Overall Summary: xxxx

Requirements:
- Ticket Label: 2-4 words
- Ticket Summary: concise and specific
- Overall Label: 2-4 words
- Overall Summary: summarize the cluster's common issue
- Keep wording operational and support-oriented

Documents:
{combined_docs}
"""

    try:
        raw_content = call_text_model(prompt, verbosity="low")
    except Exception as e:
        print(f"cluster summary failed: {e}")
        continue

    print(raw_content)

    parsed_ticket_items, overall_label, overall_summary = parse_cluster_summary(raw_content)
    ticket_sum_list.extend(parsed_ticket_items)

    cluster_id = cluster[0][1]
    ratio = len(cluster) / total_clustered_tickets if total_clustered_tickets else 0

    summary_rows.append({
        "Compound Cluster Id": cluster_id,
        "Topic": overall_label,
        "Brief Summary": overall_summary,
        "Detailed Info": raw_content,
        "Percentage Ratio": ratio
    })

summary_df = pd.DataFrame(summary_rows)

if not summary_df.empty:
    summary_df["Percentage Ratio"] = summary_df["Percentage Ratio"].apply(lambda x: f"{100 * x:.2f}%")
    summary_df = summary_df.sort_values(by=["Percentage Ratio"], ascending=[False])

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 1200)

print(summary_df)
summary_df.to_csv(OUTPUT_CLUSTER_CSV, index=False, encoding="utf-8-sig")
print("\n>> First Part Done...")

# =========================
# Step 9: Global issue classification
# =========================
raw_ticket_summary_block = ""
for item in ticket_sum_list:
    raw_ticket_summary_block += (
        f"Ticket Id: {item[0]}; "
        f"Ticket Label: {item[1]}; "
        f"Ticket Summary: {item[2]}\n"
    )

final_prompt = f"""
Below are all summarized tickets.

{raw_ticket_summary_block}

Now produce a remediation-oriented issue classification.

Output format for each issue block:
Key Issue: xxxx
Issue Summary: xxxx
Related Tickets: xxx, xxx, xxx

Use "===" to separate issue blocks.

Rules:
- Classification must be detailed.
- Classification must be non-overlapping.
- Each ticket id can appear only once across all issue blocks.
- Do not miss any ticket.
- Prefer practical support / operations issue names.
"""

final_issue_text = call_text_model(final_prompt, verbosity="low")
print(final_issue_text)

issue_rows = parse_issue_output(final_issue_text)
issue_df = pd.DataFrame(issue_rows)

if not issue_df.empty:
    issue_df["Ticket Length"] = issue_df["Ticket List"].apply(
        lambda x: len([t for t in x.split(",") if clean_text(t)])
    )
    issue_df = issue_df.sort_values(by=["Ticket Length"], ascending=[False])
    issue_df = issue_df.drop_duplicates(["Key Issue"], keep="first")

print(issue_df)
issue_df.to_csv(OUTPUT_ISSUE_CSV, index=False, encoding="utf-8-sig")
print("\n>> Second Part Done...")
