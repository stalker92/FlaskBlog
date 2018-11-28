from flaskblog import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
    from flaskblog import db
    db.create_all()
