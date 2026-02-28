from core import NanoWeb
app = NanoWeb()
@app.route("/")
async def index():
    return "<h1>welcome to simple framework</h1>"
@app.route("/user/<id>")
async def get_user(id):
    return {"user_id": id, "status": "active", "role": "admin"}
if __name__ == "__main__":
    app.run()
