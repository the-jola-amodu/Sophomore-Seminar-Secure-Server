from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
import random
import os
from string import ascii_uppercase
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'mp4'}

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

rooms = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    room = session.get("room")
    name = session.get("name")
    
    if not room or not name:
        return {"error": "Not logged in or room missing"}, 403
    
    # 1. Check if the post request has the file part
    if 'file' not in request.files:
        return {"error": "No file part"}, 400
    
    file = request.files['file']
    
    # 2. Check if user selected a file
    if file.filename == '':
        return {"error": "No selected file"}, 400
        
    if file and allowed_file(file.filename):
        # 3. Securely save the file
        filename = secure_filename(file.filename)
        # Prepend a timestamp to avoid naming collisions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        safe_filename = timestamp + filename
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        # 4. Construct the URL accessible by clients
        file_url = url_for('static', filename=f'uploads/{safe_filename}')
        _, file_extension = os.path.splitext(filename)
    
        # Create the clean display text
        if file_extension:
            # Example: "File: PNG" or "File: PDF"
            link_text = f"File: {file_extension.upper().lstrip('.')}" 
        else:
            link_text = "Download File"
        
        # Message content will be a description + a link
        content = {
            "name": name,
            "message": f"Shared: <a href='{file_url}' target='_blank' download='{filename}' class='text-gray-200 hover:underline font-semibold'>{link_text}</a>",
            "timestamp": datetime.now().strftime("%I:%M %p")
        }
        
        # Send via SocketIO
        socketio.emit('message', content, to=room)
        
        return {"success": True, "filename": filename, "url": file_url}, 200
    
    return {"error": "File type not allowed"}, 400

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        user_name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        room_name_input = request.form.get("room_name_input")

        if not user_name:
            return render_template("home.html", error="Please enter a name.", code=code, name=user_name)
        
        if join != False and not code:
            return render_template("home.html", error="Pleae enter a room code.", code=code, name=user_name)
        
        if join != False and user_name in rooms[code]["members"]:
            return render_template("home.html", error="This username is already in use in this room. Please choose another name.", code=code, name=user_name)

        room = code

        if create != False:
            room = generate_unique_code(5) 
            rooms[room] = {"name": room_name_input, "members": [], "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=user_name)

        session["room"] = room
        session["name"] = user_name
        return redirect(url_for("room"))
    return render_template("home.html", room_name_input="")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    
    room_code = session.get("room")
    room_data = rooms.get(room_code)
    room_name = room_data.get("name", f"Room {room_code}") # Use code as fallback name
    
    return render_template(
        "room.html",
        code=room_code,
        room_name=room_name,
        messages=room_data["messages"],
        name=session.get("name")
    )

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    content = {
        "name": session.get("name"),
        "message": data["data"],
        "timestamp": datetime.now().strftime("%I:%M %p")
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    if name not in rooms[room]["members"]:
        rooms[room]["members"].append(name)
        
    join_room(room)
    send({"name": "system", "message": f"{name} just walked in", "timestamp": datetime.now().strftime("%I:%M %p")}, to=room)
    emit("update_members", {"members": rooms[room]["members"]}, to=room)
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    if not room or not name or room not in rooms:
        return
    leave_room(room)

    if name in rooms[room]["members"]:
        rooms[room]["members"].remove(name)
    if len(rooms[room]["members"]) == 0:
        del rooms[room]
        print(f"% % % % % % Room {room} is empty. Incinerating ...")
    
    send({"name": "system", "message": f"{name} has left the room", "timestamp": datetime.now().strftime("%I:%M %p")}, to=room)
    emit("update_members", {"members": rooms[room]["members"]}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=50501, debug=True)
    # 192.168.137.1 