create table articles (
    pageName text primary key,
    title text unique, 
    creationDate int,
    modifiedDate int,
    body text,
    summary text,
    sourceCodeLink text,
    folder text
)