from website import create_app

app = create_app()

if __name__ == "__main__": #This line tells us that this app can only be run on running this file and not when imported on other files
    app.run(debug=True)


