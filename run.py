from app import create_app
import webview
import threading

app = create_app()

def start_flask():
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    webview.create_window(
        "BAG - Budgeting Assistance Guide",
        "http://127.0.0.1:5000"
    )

    webview.start()