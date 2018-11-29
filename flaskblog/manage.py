from flaskblog import create_app, db, manager

app = create_app()


@manager.command
def recreate_db():
    """Drops all existing data from database and creates empty database"""
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('Database is recreated.')


if __name__ == '__main__':
    manager.run()
