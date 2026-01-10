
```sql
对于那种object怎么拿数据
get_json_object(extra_info::string, "$.oktaUser['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'].employeeNumber") as emp_number,
extra_info:oktaUser['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User']:manager:displayName::string as emp_manager_name,

```

```sql
-- channel partner cases of which the ppta is only ppta
/*
create temp view id_pool as (
  select distinct
  cle.id as legal_entity_id,
  bp:personId as person_id,
  prole
  from `tp-prod-sg`.silver.authorisation__client_legal_entity as cle
  left join `tp-prod-sg`.silver.authorisation__business_profile as bp on bp.id = cle.data:profileId::string
  lateral view outer explode(cast(bp.data:businessPeople as array<string>)) as bp
  lateral view outer explode(cast(from_json(bp:roles, 'array<string>') as array<string>)) as prole  -- 第一个是告诉解析器JSON的结构，第二个是确保类型转换的精确性。在处理不确定的JSON数据时增加了代码的健壮性。
  -- LATERAL VIEW是在JOIN之后执行的，所以不能直接在LATERAL VIEW后跟JOIN
);

create temp view account_pool as (
  select distinct
  cast(sf.legal_entity_id as string) as legal_entity_id,
  cast(ac.id as string) as account_id,
  ac.`data`:accountDetails:businessDetails.businessName?::string as biz_name_local,
  ac.`data`:clientInternalInfo:owningEntity?::string as owning_entity,
  timestamp(ac.`data`:kycRecord:receiveTime) as kyc_receive_time,
  timestamp(ac.`data`:kycRecord:kycPassedDate) as kyc_pass_time,
  ac.`data`:kycRecord:status?::string as kyc_status,
  ac.`data`:status?::string as account_status,
  ac.`data`:clientInternalInfo:signUpUtm:utmSource?::string as utm_source,
  ac.`data`:clientInternalInfo:signUpUtm:utmCampaign?::string as utm_campaign,
  ac.`data`:clientInternalInfo:signUpOwner is not null as bd_initiate
  from `tp-prod-sg`.`silver`.`authorisation__account` as ac
  left join `tp-prod-sg`.`silver`.`airboard_ng_api__salesforce_data` as sf on sf.account_id = ac.id
  where 1 = 1
  and ac.`data`:clientInternalInfo.owningEntity?::string in ('Airwallex (Hong Kong) Limited', 'Airwallex (Singapore) Pte Ltd', 'Airwallex (Malaysia) Sdn. Bhd.')
  and left(sf.`data`:ownerOrgLevel2, 2) <> 'CN'
  and lower(ac.`data`:clientInternalInfo:signUpUtm:utmSource) = 'partnerstack'
  and ac.`data`:kycRecord:status?::string = 'SUCCESS'
  and ac.`data`:status?::string in ('ACTIVE', 'DORMANT')
);
select * from account_pool;

create temp view role_details as (
  select distinct
  ip.*,
  concat_ws(' ', pp.data:personDetails:name:firstName:local::string, pp.data:personDetails:name:lastName:local::string) as person_name_local
  from id_pool as ip
  inner join account_pool as ap on ap.legal_entity_id = ip.legal_entity_id
  left join `tp-prod-sg`.silver.authorisation__person_profile as pp on pp.id = ip.person_id
);

select 
legal_entity_id,
person_id,
person_name_local,
listagg(distinct prole, ",") as roles_1,
string_agg(distinct prole, ",") as roles_2
from role_details
group by 1, 2, 3
having roles_2 = 'AUTHORIZED_PERSON'
*/

-- Channel Partner Sign-up On Behalf
/*
select distinct
kc.`data`:kycRecordId?::string as legal_entity_id,
ke.`data`:onboardDetails:createdByRole?::string as created_by_role
from `risk-prod-sg`.`silver`.`individualkyc__kyc_case` as kc
left join `risk-prod-sg`.`silver`.`individualkyc__kyc_entity` as ke on kc.`data`:entityId?::string = ke.id
where 1 = 1
and ke.`data`:onboardDetails:createdByRole::string = '00000000-0000-0000-0000-000000040000'  -- "Channel Partner", "渠道合作方。"
*/
```

```sql
-- airboard auth users
create or replace view yikai_test_dbt.temp as (select
  email as emp_email,
  `id` as emp_id,
  active,
  deleted,
  get_json_object(extra_info::string, "$.oktaUser['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'].employeeNumber") as emp_number,
  get_json_object(extra_info::string, "$.oktaUser['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'].department") as emp_team,
  get_json_object(extra_info::string, "$.oktaUser['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'].manager.value") as emp_manager
from 
  `tp-prod-sg`.silver.airboardngauth__account
where 
  1 = 1
  and not deleted
  and not frozen
);
```

```sql
-- pivot for string
select * from (
select legal_entity_id, maker, level_new
from tt)
pivot(concat_ws(',', collect_list(maker)) for level_new in ('L1' as `maker`, 'L2' as checker, 'L3' as compliance))
/*
collect_list(maker) 是 pivot 需要的聚合（把多行变成一个结果）
concat_ws 是对聚合结果做“格式化”（数组→字符串），它本身不是聚合，但包在外面也没问题，因为整体表达式里包含聚合。
array_agg 当然也可以
*/
```
