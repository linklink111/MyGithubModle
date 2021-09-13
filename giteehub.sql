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



