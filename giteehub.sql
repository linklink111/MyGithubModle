create table "user"(
	id int primary key,
	login varchar(255),
	name varchar(255),
	company varchar(255),
	email varchar(255),
	created_at timestamp,
	type varchar(255),
	fake int check (fake >= 0 and fake <= 255),
	deleted int check (deleted >= 0 and deleted <= 255),
	long decimal(11,8),
	lat decimal(10,8),
	country_code char(3),
	state varchar(255),
	city  varchar(255)
)

drop table "user"

create table project(
	id int primary key,
	url varchar(255),
	owner_id int references "user"(id),
	name varchar(255),
	descriptior varchar(255),
	language varchar(255),
	created_at varchar(255),
	forked_from int references project(id),
	deleted int,
	updated_at timestamp
)

create table organization_members(
	org_id int,
	user_id int references "user"(id),
	created_at timestamp
)

drop table organization_members

create table followers(
	user_id int references "user"(id),
	follower_id int references "user"(id),
	created_at timestamp
) 

drop table followers

create table watchers(
	repo_id int references project(id),
	user_id int references "user"(id),
	created_at timestamp
)

create table star_at(
	repo_id int references project(id),
	user_id int references "user"(id),
	created_at timestamp
)

create table repo_milestones(
	id int,
	repo_id int references project(id),
	name varchar(24)
)

create table project_language(
	project_id int references project(id),
	language varchar(255),
	bytes int,
	created_at timestamp
)

create table project_members(
	repo_id int references project(id),
	user_id int references "user"(id),
	created_at timestamp,
	ext_ref_id varchar(24)
)

create table repo_labels(
	id int primary key,
	repo_id int references project(id),
	name varchar(24)
)

drop table repo_labels

create table commits(
	id int primary key,
	sha varchar(40),
	author_id int references "user"(id),
	commiter_id int references "user"(id),
	project_id int references project(id),
	created_at timestamp
)

create table project_commits(
	project_id int references project(id),
	commit_id int references commits(id) 
)

create table pull_request(
	id int primary key,
	head_repo_id int references project(id),
	base_repo_id int references project(id),
	head_commit_id int references commits(id),
	base_commit_id int references commits(id),
	pullreq_id int,
	intra_branch int
	
)

drop table pull_request

create table commit_parents(
	commit_id int references commits(id),
	parent_id int references commits(id)
)

create table commit_comments(
	id int primary key,
	commit_id int references commits(id),
	user_id int references "user"(id),
	body varchar(256),
	line int,
	position int,
	comment_id int,
	created_at timestamp
)

create table issues(
	id int primary key,
	repo_id int references project(id),
	reporter_id int references "user"(id),
	assignee_id int references "user"(id),
	issue_id text,
	pull_request int,
	pull_request_id int references pull_request(id),
	created_at timestamp
)

create table pull_request_commits(
	pull_request_id int references pull_request(id),
	commit_id int references commits(id)
)

create table pull_request_comments(
	pull_request_id int references pull_request(id),
	user_id int references "user"(id),
	comment_id text,
	position int,
	body varchar(256),
	commit_id int references commits(id),
	created_at timestamp
)


create table pull_request_history(
	id int,
	pull_request_id int references pull_request(id),
	created_at timestamp,
	action varchar(255),
	actor_id int references "user"(id)

)

create table issue_comments(
	issue_id int references issues(id),
	user_id int references "user"(id),
	comment_id text,
	created_at timestamp
)

create table issue_events(
	event_id text,
	issue_id int references issues(id),
	actor_id int references "user"(id),
	action varchar(255),
	action_specified varchar(255),
	created_at timestamp
)

create table issue_labels(
	label_id int references repo_labels(id),
	issue_id int references issues(id)
)
-- indexs

CREATE UNIQUE INDEX login ON "user" (login ASC);
CREATE UNIQUE INDEX sha ON commits (sha ASC);
CREATE UNIQUE INDEX comment_id ON commit_comments (comment_id ASC);
CREATE INDEX follower_id ON followers (follower_id ASC);
CREATE UNIQUE INDEX pullreq_id ON pull_request (pullreq_id ASC, base_repo_id ASC);
CREATE INDEX name ON project (name ASC);
CREATE INDEX commit_id ON project_commits (commit_id ASC);
CREATE INDEX project_id ON project_language (project_id);

-- 存储过程
-- 查询一天内/一周内/一星期内新增的仓库
-- 1 : 一天内， 2 : 一周内，3 : 一个月内
-- 由于github api没有给出仓库star数量的接口，所以这里暂时不排序了
drop function list_by_star(time_type int); 
create or replace function list_by_star(time_type int) 
returns TABLE (
      id int,
	  name varchar(255),
	  descriptior varchar(255)
)
as $$
declare
	time_gap varchar;
begin
	if time_type = 1 then time_gap = '1 day'; end if;
	if time_type = 2 then time_gap = '1 week'; end if;
	if time_type = 3 then time_gap = '1 month'; end if;
	if time_type = 4 then time_gap = '3 month'; end if;
	if time_type = 5 then time_gap = '1 year'; end if;
	return query
	select project.id,project.name,project.descriptior from project
	where created_at::date > ((select current_timestamp)::date - time_gap::interval);
end;
$$ language plpgsql;
-- 新增仓库的数量
drop function increase_count(time_type int); 
create or replace function list_by_star(time_type int) 
returns TABLE (
      id int,
	  name varchar(255),
	  descriptior varchar(255)
)
as $$
declare
	time_gap varchar;
begin
	if time_type = 1 then time_gap = '1 day'; end if;
	if time_type = 2 then time_gap = '1 week'; end if;
	if time_type = 3 then time_gap = '1 month'; end if;
	if time_type = 4 then time_gap = '3 month'; end if;
	if time_type = 5 then time_gap = '1 year'; end if;
	return query
	select count(project.id) from project
	where created_at::date > ((select current_timestamp)::date - time_gap::interval);
end;
$$ language plpgsql;

-- 查询这一天/周/月比上一天/周/月新增的仓库数量

create or replace function increase_count(time_type int) 
returns int
as $$
declare
	time_gap varchar;
	cnt1 int;
	cnt2 int;
begin
	if time_type = 1 then time_gap = '1 day'; end if;
	if time_type = 2 then time_gap = '1 week'; end if;
	if time_type = 3 then time_gap = '1 month'; end if;
	if time_type = 4 then time_gap = '3 month'; end if;
	if time_type = 5 then time_gap = '1 year'; end if;
	select count(project.id) from project
	where created_at::date > ((select current_timestamp)::date - time_gap::interval)
	into cnt1;
	select count(project.id) from project
	where created_at::date < ((select current_timestamp)::date - time_gap::interval)
	and created_at::date > ((select current_timestamp)::date - time_gap::interval*2)
	into cnt2;
	return cnt1 - cnt2;
end;
$$ language plpgsql;

select increase_count(3)

select increase_count(4)

select current_timestamp::date

select created_at::date from project

select created_at::date from project

select list_by_star(3);
-- 查询这个月比上个月新增了多少仓库
select increase_count(3);

-- 查询特定语言的仓库，按获得的star降序排序；
select * from project
create or replace function repo_of_language(target_language varchar ) 
returns TABLE (
      id int,
	  name varchar(255),
	  descriptior varchar(255)
)
as $$
declare
	time_gap varchar;
begin
	return query
	select project.id,project.name,project.descriptior from project
	where language = target_language;
end;
$$ language plpgsql;

select repo_of_language('JavaScript')

-- 一些常用的查询语句, 有需要可以修改参数进行查询
select * from project

create or replace function most_commit_area() 
returns TABLE (
      country_code int,
	  count int
)
as $$
declare
	time_gap varchar;
begin
	select u.country_code, count(*) 
	from commits c, "user" u
	where c.author_id = u.id 
	and date(c.created_at) = date(now())
	group by u.country_code;
end;
$$ language plpgsql;
select most_commit_area();
-- 1. 查询今天最多的 commit 来自哪个地区
select u.country_code, count(*) 
from commits c, users u
where c.author_id = u.id 
and date(c.created_at) = date(now())
group by u.country_code

-- 2.查询最近三个月最活跃的组织
select distinct(u.login) as login
	from commits c, users u, project_commits pc, users u1, project p
	where u.id = c.committer_id
		and u.fake is false
      	and pc.commit_id = c.id
      	and pc.project_id = p.id
      	and p.owner_id = u1.id
      	and p.name = 'rails'
      	and u1.login = 'rails'
      	and c.created_at > DATE_SUB(NOW(), INTERVAL 3 MONTH)
union
select distinct(u.login) as login
  from pull_requests pr, projects p, users u, users u1, pull_request_history prh
  where u.id = prh.actor_id
    and prh.action = 'merged'
    and u1.id = p.owner_id
    and prh.pull_request_id = pr.id
    and pr.base_repo_id = p.id
    and prh.created_at > DATE_SUB(NOW(), INTERVAL 3 MONTH)
    and p.name = 'rails'
    and u1.login = 'rails'


create or replace function active_org() 
returns TABLE (
      login varchar(255)
)
as $$
declare
	time_gap varchar;
begin
	return query
	select distinct(u.login) as login
		from commits c, "user" u, project_commits pc, "user" u1, project p
		where u.id = c.committer_id
			and u.fake is false
      		and pc.commit_id = c.id
      		and pc.project_id = p.id
      		and p.owner_id = u1.id
      		and p.name = 'rails'
      		and u1.login = 'rails'
      		and c.created_at > DATE_SUB(NOW(), INTERVAL 3 MONTH)
	union
	select distinct(u.login) as login
  	from pull_requests pr, projects p, "user" u, "user" u1, pull_request_history prh
  	where u.id = prh.actor_id
    	and prh.action = 'merged'
    	and u1.id = p.owner_id
    	and prh.pull_request_id = pr.id
    	and pr.base_repo_id = p.id
    	and prh.created_at > DATE_SUB(NOW(), INTERVAL 3 MONTH)
    	and p.name = 'rails'
    	and u1.login = 'rails';
	end;
$$ language plpgsql;
-- 查询 Ruby 或 Rails 语言使用的最新计数

select *
from project_languages
where project_id = 1334
order by created_at desc

-- 列出一个仓库所有的commits

create or replace function active_org() 
returns TABLE (
      id int primary key,
	sha varchar(40),
	author_id int ,
	commiter_id int,
	project_id int,
	created_at timestamp
)
as $$
declare
	time_gap varchar;
begin
	return query
	select c.*
	from commits c, project_commits pc, projects p, users u
	where u.login = 'rails'
  	and p.name = 'rails'
  	and p.id = pc.project_id
  	and c.id = pc.commit_id
	order by c.created_at desc;
end;
$$ language plpgsql;

-- 查询一个 pull request 中的所有action
create or replace function active_org() 
returns TABLE (
      action varchar(255),
	created_at varchar(255),
	login varcher(255)
)
as $$
declare
	time_gap varchar;
begin
	return query
select user, action, created_at from
(
  select prh.action as action, prh.created_at as created_at, u.login as user
  from pull_request_history prh, users u
  where prh.pull_request_id = ?
    and prh.actor_id = u.id
  union
  select ie.action as action, ie.created_at as created_at, u.login as user
  from issues i, issue_events ie, users u
  where ie.issue_id = i.id
    and i.pull_request_id = ?
    and ie.actor_id = u.id
  union
  select 'discussed' as action, ic.created_at as created_at, u.login as user
  from issues i, issue_comments ic, users u
  where ic.issue_id = i.id
    and u.id = ic.user_id
    and i.pull_request_id = ?
  union
  select 'reviewed' as action, prc.created_at as created_at, u.login as user
  from pull_request_comments prc, users u
  where prc.user_id = u.id
    and prc.pull_request_id = ?
) as actions
order by created_at;
end;
$$ language plpgsql;
-- 获取一个 issue 或 pull request 的所有参与者

select distinct(user_id) from
(
  select user_id
  from pull_request_comments
  where pull_request_id = ?
  union
  select user_id
  from issue_comments ic, issues i
  where i.id = ic.issue_id and i.pull_request_id = ?
) as participants

-- 获取一天内 NL 国家提交了 java 项目 commit 的用户

select u.login
from users u, commits c, projects p, project_commits pc
where date(c.created_at) = date(now())
and pc.commit_id = c.id
and c.author_id = u.id
and u.country_code = 'nl'
and 'java' = (select pl.language
              from project_langauges pl
              where pl.project_id = p.id
              order by pl.created_at desc, pl.bytes desc
              limit 1)


-- 获取x天前的仓库数量，x可以指定
create or replace function num_days_ago(days int) 
returns int
as $$
declare
	time_gap varchar;
	cnt1 int;
	cnt2 int;
begin
	select count(project.id) from project
	where created_at::date > ((select current_timestamp)::date - '1 day'::interval*(days-1))
	into cnt1;
	select count(project.id) from project
	where  created_at::date > ((select current_timestamp)::date - '1 day'::interval*(days))
	into cnt2;
	return cnt1 - cnt2;
end;
$$ language plpgsql;


			  
select * from "user"

select * from project

select list_by_star(3)