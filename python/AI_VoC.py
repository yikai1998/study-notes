# coding=gbk
"""
这代码是在用 OpenAI embedding + GPT + KMeans，把一批工单自动做成 聚类分析、摘要总结、问题分类、报表导出。
"""
import os
# import time
from openai import OpenAI
import json
import pickle
import numpy as np
from sklearn.cluster import KMeans
# from sklearn.metrics import silhouette_score
import pandas as pd
import re

route1 = os.path.join(os.path.expanduser("~"), 'Downloads') + '/'
route2 = os.path.join(os.path.expanduser("~"), 'Desktop') + '/'

"""openai api key of myself"""
llm = OpenAI(api_key='sk-xxx')


"""reference of manual inputs"""
reference_ans = {}
with open('correct_manual_record_202405.json') as answer:
    raw = json.load(answer)
    for i in raw:
        reference_ans.update({i['Ticket ID']: [i['Key Issue'], i['Issue Summary']]})

"""load tickets and have a store in tickets"""
tickets = []
# update_despn = lambda row: f">> Mail Subject: {row['Subject']} \n>> Mail Content: {row['Description']}"
update_despn = lambda row: f"{row['Subject']} \t {re.sub(r'\s+', ' ', row['Description']).strip()}"
with open(file='TicketsCard_202405.json') as ff:
    ticket_info = json.load(ff)
    for ticket in ticket_info[:100]:
        id = ticket['Ticket ID']
        ticket['Description'] = update_despn(ticket)
        if id in reference_ans.keys():
            ticket['Description'] = f'This is about {reference_ans[id][0]}-{reference_ans[id][1]}; '+ticket['Description']
        description = ticket['Description']
        tickets.append((id, description))


"""helper for generating embeddings"""
class EmbeddingHelper():
    # communicate with the OpenAI API to generate an embedding for the given text
    # embeddings are vectors created by machine learning models for the purpose of capturing meaningful data about each object
    def __init__(self):
        self.client = llm  # by default; be accessible to all methods of the class via the self reference

    def get_embedding(self, text, model='text-embedding-ada-002'):
        text = re.sub(r'\s+', ' ', text).strip()
        return self.client.embeddings.create(input=[text[:8000]], model=model)

embeddings_helper = EmbeddingHelper()


"""helper for simple summarizations"""
class SummaryHelper():
    def get_summary(self, text_to_summarize):
        text_to_summarize = re.sub(r'\s+', ' ', text_to_summarize).strip()
        prompt = f"Please summarize the following text:\n{text_to_summarize[:8000]}"
        response = llm.chat.completions.create(
            model='gpt-4o',  # Use the most capable model for summarization
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=150,  # You can adjust the number of tokens based on how long you want the summary to be
            temperature=0.1,  # A lower temperature makes the response more deterministic and less creative
        )
        return response

summary_helper = SummaryHelper()


"""helper to get an optimal number of clusters"""
def determine_optimal_clusters(data, max_k):
    inertias = []
    for i in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(data)
        inertias.append(kmeans.inertia_)

    # Calculate the differences in inertia
    diffs = np.diff(inertias)
    diff_in_diff = np.diff(diffs)

    optimal_k = np.argmax(diff_in_diff) + 2  # Because np.diff reduces the length, and we look for the elbow
    return optimal_k




"""get embeddings for each subject and request form tickets,
and store them locally in order to reduce openAI billing costs"""
file = 'embeddings_v6_0612.pickle'
embeddings_map = {}
try:
    with open(file, 'rb') as handle:
        # Opens a file only for reading but in a binary format
        embeddings_map = pickle.load(handle)
        print('loaded embeddings from %s' %file)
except:
    print('%s not found' %file)

for (id, description) in tickets:
    if id not in embeddings_map:
        print('getting embedding for: %s %s' % (id, description[:50]))

        try:
            # subject_embedding = embeddings_helper.get_embedding(subject).data[0].embedding  # embedding for ticket summary
            description_embedding = embeddings_helper.get_embedding(description).data[0].embedding  # embedding for ticket description
            description_summary = summary_helper.get_summary(description).choices[0].message.content  # summary of ticket description
        except Exception as e:
            print('error fetching: %s %s' % (id, description[:50]))
            print(e)
            continue

        data = (id, description_embedding, description_summary, description)
        embeddings_map[id] = data

        with open(file, 'wb') as handle:
            pickle.dump(embeddings_map, handle, protocol=pickle.HIGHEST_PROTOCOL)


items = [
    embeddings_map[k] for k in embeddings_map
]
embeddings = np.array(
    [np.array(despn_emb) for id, despn_emb, despn_sum, despn in items[:]]
)  # a 2D NumPy array or a list of lists where each sub-list represents an embedding (or a high-dimensional point)

# Determine the optimal number of main type clusters
optimal_main_clusters = determine_optimal_clusters(embeddings, max_k=10)

# Cluster to determine types
clusterer_type = KMeans(n_clusters=optimal_main_clusters, random_state=42)
type_labels = clusterer_type.fit_predict(embeddings)

# Initialize a list to hold the subtype labels
subtype_2nd_labels = np.empty_like(type_labels)
subtype_3rd_labels = np.empty_like(type_labels)

# Loop over each type cluster and perform second layer clustering for each
for type_label in np.unique(type_labels):
    type_cluster_embeddings = embeddings[type_labels == type_label]  # boolean indexing in np array

    # Make sure there are enough samples to form subclusters
    if len(type_cluster_embeddings) >= 2:  # Minimum samples needed to form at least 2 subclusters
        optimal_sub_clusters = determine_optimal_clusters(type_cluster_embeddings,
                                                          max_k=min(len(type_cluster_embeddings), 10))

        if optimal_sub_clusters > 1:  # We can only cluster if we have more than one cluster
            clusterer_subtype = KMeans(n_clusters=optimal_sub_clusters, random_state=42)
            sub_labels = clusterer_subtype.fit_predict(type_cluster_embeddings)
        else:
            sub_labels = np.zeros(
                len(type_cluster_embeddings))  # Assign all to a single cluster if only one cluster is optimal
    else:
        sub_labels = np.zeros(len(type_cluster_embeddings))  # Assign all to a single cluster if not enough samples

    # Save the subtype labels in your main labels array
    subtype_2nd_labels[type_labels == type_label] = sub_labels
combined_12_labels = type_labels * 100 + subtype_2nd_labels  # Example combination

# Loop over each type cluster and perform third layer clustering for each
for type_2nd_label in np.unique(combined_12_labels):
    type_cluster_embeddings = embeddings[combined_12_labels == type_2nd_label]

    # Make sure there are enough samples to form subclusters
    if len(type_cluster_embeddings) >= 2:  # Minimum samples needed to form at least 2 subclusters
        optimal_sub_clusters = determine_optimal_clusters(type_cluster_embeddings,
                                                          max_k=min(len(type_cluster_embeddings), 10))

        if optimal_sub_clusters > 1:  # We can only cluster if we have more than one cluster
            clusterer_subtype = KMeans(n_clusters=optimal_sub_clusters, random_state=42)
            sub_labels = clusterer_subtype.fit_predict(type_cluster_embeddings)
        else:
            sub_labels = np.zeros(
                len(type_cluster_embeddings))  # Assign all to a single cluster if only one cluster is optimal
    else:
        sub_labels = np.zeros(len(type_cluster_embeddings))  # Assign all to a single cluster if not enough samples

    # Save the subtype labels in your main labels array
    subtype_3rd_labels[combined_12_labels == type_2nd_label] = sub_labels

# Combine the type and subtype labels
combined_agg_labels = list(zip(type_labels, subtype_2nd_labels, subtype_3rd_labels))
# print(combined_agg_labels)


comp_lvl_cluster = {}
ticket_cluster_map = {}

for i in range(0, len(combined_agg_labels)):
    label = '-'.join(map(str, combined_agg_labels[i]))
    id, description_embedding, description_summary, description = items[i]
    ticket_cluster_map[id] = combined_agg_labels[i]
    if label not in comp_lvl_cluster:
        comp_lvl_cluster[label] = []
    comp_lvl_cluster[label].append((id, label, description_summary))  # append the related list behind each unique label element
sorted_comp_lvl_clusters = sorted([comp_lvl_cluster[k] for k in comp_lvl_cluster], key=lambda k: len(k), reverse=True) # top1 is the cluster with most amount
# print([len(c) for c in sorted_comp_lvl_clusters])  # freq list of these detailed clusters list
print(ticket_cluster_map)
# print(sorted_comp_lvl_clusters)

summary_df = pd.DataFrame({
    'Compound Cluster Id': [],
    'Topic': [],
    'Brief Summary': [],
    'Detailed Info': [],
    'Percentage Ratio': []
})

conversation_history = []
ticket_sum_list = []

for cluster in sorted_comp_lvl_clusters[:]:
    if len(cluster) < 3:
        print('>> Too short, skip')
        continue
    descriptions = [f'ticket_id is {id} \n{description_summary}' for id, label, description_summary in cluster]

    combined_descriptions = '--------------'.join(descriptions)

    # the placeholder {text} will be replaced by actual content when the template is used. The instructions within the template guide the language model on how to process the text
    prompt_template = f"""
    each document is separated by "----------------".
    Firstly,
    extract the ticket_id number from the beginning of each document, started with 'Ticket Id: '
    and write a two/three word label for each document, started with 'Ticket Label: '
    and concise the summary for each document, started with 'Ticket Summary: ';
    which means, please follow the output template of
    "Ticket Id: xxxx{'\n'}Ticket Label: xxxx{'\n'}Ticket Summary: xxxx"
    
    Secondly, 
    provide a concise overall conclusion of all documents and a two or three word-label for all documents, following the output template of 
    "Overall Label: xxxx{'\n'}Overall Summary: xxxx"

    {combined_descriptions}
    """

    response = llm.chat.completions.create(
        model='gpt-4o',  # Use the most capable model for summarization
        messages=[
            {'role': 'user', 'content': prompt_template}
        ],
        # max_tokens=150,  # You can adjust the number of tokens based on how long you want the summary to be
        temperature=0.1,  # A lower temperature makes the response more deterministic and less creative
    )
    raw_content = response.choices[0].message.content
    print(raw_content)

    raw_content = raw_content.replace('*', '').replace('#', '')
    match_pattern = re.compile(r"""
        Ticket\s+Id:\s*(\d+)\s*
        Ticket\s+Label:\s*(.*?)\s*
        Ticket\s+Summary:\s*(.*?)(?=\n|$)
""", re.VERBOSE)
    matches = match_pattern.findall(raw_content)
    ticket_sum_list += matches

    raw_content = raw_content.split('\n')

    # print(re.split('Overall Label: (.*)Overall Summary: (.*)', str(raw_content)))
    cluster_id = cluster[0][1]
    overall_label = ''
    overall_summary = ''
    for item in raw_content:
        if item.count('Overall Label:') > 0:
            try:
                overall_label = re.findall('Overall Label: (.*)', item)[0]
            except:
                overall_label = raw_content[-2]
    for item in raw_content:
        if item.count('Overall Summary:') > 0:
            try:
                overall_summary = re.findall('Overall Summary: (.*)', item)[0]
            except:
                overall_summary = raw_content[-1]
    # overall_summary = re.findall('Overall Summary: (.*)', raw_content[-1])[0]
    overall_partio = len(cluster) / sum([len(c) for c in sorted_comp_lvl_clusters])
    new_row = pd.DataFrame({
        'Compound Cluster Id': [cluster_id],
        'Topic': [overall_label],
        'Brief Summary': [overall_summary],
        'Detailed Info': [response.choices[0].message.content],
        'Percentage Ratio': [overall_partio]
    })
    summary_df = pd.concat([summary_df, new_row], ignore_index=True)

pd.set_option('display.max_columns',None)
pd.set_option('display.max_rows',None)
pd.set_option('display.width',1000)

print(summary_df)
summary_df['Percentage Ratio'] = summary_df['Percentage Ratio'].apply(lambda x: '%.2f%%' %(100*x))
summary_df = summary_df.sort_values(by=['Percentage Ratio'], ascending=[False])
summary_df.to_csv('ai_output1.csv')
print('\n>> First Part Done...')

raw_content_wording = ''
for item in ticket_sum_list:
    raw_content_wording += f"""Ticket Id: {item[0]};Ticket Label: {item[1]};Ticket Summary: {item[2]}{'\n'}"""

# Append the AI's response to the conversation history
conversation_history.append({'role': 'assistant', 'content': raw_content_wording})

prompt_template = """
    Finally,
    we want to make remediation based on these responses, could you help summarize and list the issues noted all above?
     
    the classification of issues should be as detailed as possible;
    
    all the tickets noted above must be taken into consideration, following the output template of 
    "Key Issue: xxxx{'\n'}Issue Summary: xxxx{'\n'}Related Tickets: xxx, xxx, xxx";
    
    each part should be separated by "===";
    
    you must avoid any redundancy and overlap in the classification of the issues (ensure the classification to be refined and non-overlapping),
    please refine the classification to ensure each key issue has a unique set of related tickets,
    also, each ticket id should only happen once in all issues classification;
    
    remember not to miss any ticket above during classifying
    
    thanks!
    """

conversation_history.append({'role': 'user', 'content': prompt_template})
response = llm.chat.completions.create(
    model='gpt-4o',  # Use the most capable model for summarization
    messages=conversation_history,  # Pass the entire conversation history
    temperature=0.5,  # A lower temperature makes the response more deterministic and less creative
)
raw_content = response.choices[0].message.content
print(raw_content)

conversation_history.append({'role': 'assistant', 'content': raw_content})

input_string = raw_content[:]
key_issue = []
issue_summary = []
related_tickets = []
issue_pattern = re.compile(r'Key Issue:\s*(.*?)\n')
summary_pattern = re.compile(r'Issue Summary:\s*(.*?)\n')
tickets_pattern = re.compile(r'Related Tickets:\s*(.*?)(?=\n|$)')
key_issue = issue_pattern.findall(input_string)
issue_summary = summary_pattern.findall(input_string)
related_tickets = tickets_pattern.findall(input_string)

# key_issue_pattern = re.compile(r'.*Key Issue: (.+)')
# current_key_issue = None
# for line in input_string.split('\n'):
#     key_issue_match = key_issue_pattern.match(line)
#
#     if key_issue_match:
#         current_key_issue = key_issue_match.group(1)
#     elif line.startswith('Issue Summary:'):
#         issue_summary_text = line.replace('Issue Summary: ', '').strip()
#     elif line.startswith('Related Tickets:'):
#         related_tickets_text = line.replace('Related Tickets: ', '').strip()

        # Store the extracted information
        # key_issue.append(current_key_issue)
        # issue_summary.append(issue_summary_text)
        # related_tickets.append(related_tickets_text)

df_data = {
    'Key Issue': key_issue,
    'Issue Summary': issue_summary,
    'Ticket List': related_tickets
}

df_data = pd.DataFrame(df_data)
df_data['Ticket Length'] = df_data['Ticket List'].apply(lambda x: len(x.split(', ')))
df_data = df_data.sort_values(by=['Ticket Length'], ascending=[False])
df_data = df_data.drop_duplicates(['Key Issue'], keep='first')
print(df_data)
df_data.to_csv('ai_output2.csv')
print('\n>> Second Part Done...')

'''
while True:
    prompt_template = input('\n>> Send a message: ')

    conversation_history.append({'role': 'user', 'content': prompt_template})

    response = llm.chat.completions.create(
        model='gpt-4o',  # Use the most capable model for summarization
        messages=conversation_history,  # Pass the entire conversation history
        # max_tokens=150,  # You can adjust the number of tokens based on how long you want the summary to be
        temperature=0.5,  # A lower temperature makes the response more deterministic and less creative
    )

    # Extract the AI's message
    raw_content = response.choices[0].message.content

    # Append the AI's response to the conversation history
    conversation_history.append({'role': 'assistant', 'content': raw_content})

    # Print the AI's response
    print('\n>> Response from ChatBot:')
    print(raw_content)

    time.sleep(1)
    _ = input('>> Press any key to continue, or type in "q" to leave')
    if _ == 'q': break'''
