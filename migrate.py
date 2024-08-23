from proxy import app, db

with app.app_context():
    # db.drop_all()
    print('Running migrations...')
    db.create_all()
