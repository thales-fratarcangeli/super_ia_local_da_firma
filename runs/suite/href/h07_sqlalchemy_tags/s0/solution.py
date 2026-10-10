from sqlalchemy import Column, ForeignKey, String, Table, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

class Base(DeclarativeBase):
    pass

post_tags = Table("post_tags", Base.metadata,
                  Column("post_id", ForeignKey("posts.id"), primary_key=True),
                  Column("tag_id", ForeignKey("tags.id"), primary_key=True))

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    posts: Mapped[list[Post]] = relationship(secondary=post_tags, back_populates="tags")

def make_session(url="sqlite://"):
    e = create_engine(url)
    Base.metadata.create_all(e)
    return Session(e)

def tag_post(session, post, names):
    for name in dict.fromkeys(names):
        tag = session.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.flush()
        if tag not in post.tags:
            post.tags.append(tag)
