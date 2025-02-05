from application.app import app, create_db

if __name__ == "__main__":
    # This lines should be executed before running the app 
                #  !!
                #  !!
                # \!!/
                #  \/
    
    
    # with app.app_context():
    #     create_db()
    app.run(debug=True)
    