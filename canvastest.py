print("The service is on")

from aiohttp import web
import json
import socketio
from random import *
import math

playerkey="chujwie"
mgkey="lelz"
mgsid = "-1"
menacingState = 0
entitiesList = []

for x in range(16):
    entitiesList.append(["0","","","Jurgend","White Room","Jorguś","[WR]"])

sio = socketio.AsyncServer()
app = web.Application()
#app = socketio.ASGIApp(sio, static_files=static_files)
sio.attach(app)

async def index(request):
    with open('canvastest.html') as f1:
        return web.Response(text=f1.read(), content_type='text/html')

@sio.event
async def connect(sid, environ):
    print("> Request From: ",sid)
    await sio.emit("syncronize",entitiesList,sid)

@sio.event
async def entityrequest(sid, data):
    if(data == 1):
        for x in range(8):
            if(entitiesList[x][0] == "0"):
                entitiesList[x][0] = "1"
                await sio.emit("newEntity", x)
                return
    else:
        for x in range(8):
            if(entitiesList[x+8][0] == "0"):
                entitiesList[x+8][0] = "1"
                await sio.emit("newFriendlyEntity", x)
                return


@sio.event
async def label(sid, data):
    await sio.emit("labelUpdated", data)
    if(data[0][0] == 'c'):
        if(data[0][4] == 'f'):
            entitiesList[int(data[0][5])][5], entitiesList[int(data[0][5])][6] = data[1], data[2]
        else:
            entitiesList[int(data[0][5]) +8][5], entitiesList[int(data[0][5]) +8][6] = data[1], data[2]
    elif(data[0][0] == 'p'):
        entitiesList[int(data[0][1]) +8][5], entitiesList[int(data[0][1]) +8][6] = data[1], data[2]
    else:
        entitiesList[int(data[0][1]) +8][5], entitiesList[int(data[0][1]) +8][6] = data[1], data[2]

@sio.event
async def removeFoe(sid, data):
    entitiesList[data] = ["0","","","Jurgend","White Room","Jorguś","[WR]"]
    await sio.emit("removeEntity", data)

@sio.event
async def removeFriend(sid, data):
    entitiesList[data+8] = ["0","","","Jurgend","White Room","Jorguś","[WR]"]
    await sio.emit("removeFriendlyEntity", data)


@sio.event
async def disconnect(sid):
    print('> Disconnect: ', sid)
    for x in range(8):
        if(entitiesList[x+8][0] == sid):
            entitiesList[x+8][0] = "0"
            await sio.emit("removeFriendlyEntity", x)
            return

@sio.event
async def drag(sid, data):
    await sio.emit("updatedPosition", data)
    if(data[0][4] == 'f'):
        entitiesList[int(data[0][5])][1], entitiesList[int(data[0][5])][2] = data[1], data[2]
    else:
        entitiesList[int(data[0][5])+8][1], entitiesList[int(data[0][5]) + 8][2] = data[1], data[2]

@sio.event
async def loginrequest(sid, data):
    print("-> New Credentials")
    print("-> Sid: "+sid)
    print("-> User Name :     "+data[0])
    print("-> Character Name: "+data[1])
    print("-> Key:            "+data[2])
    if(data[2] == playerkey or data[2] == mgkey):
        print("-> User logged as player")
        for x in range(8):
            if(entitiesList[x+8][0] == "0"):
                print("--> Login success")
                await sio.emit('newPlayerEntity', [x, data[0], data[1]])
                await sio.emit('accessGranted', "1", sid)
                entitiesList[x+8][0] = sid
                entitiesList[x+8][3] = entitiesList[x+8][5] = data[0]
                entitiesList[x+8][4] = entitiesList[x+8][6] = data[1]
                if(data[2] == mgkey):
                    mgsid = sid
                    print(mgsid)
                    await sio.emit("gmApproved", 0, mgsid)
                    print("---> MG!")
                return
        print("-> No slots left")
        await sio.emit('accessGranted', "-5", sid)
    else:
        print("-> User fucked up authentication")
        await sio.emit('accessGranted', "-4", sid)

#async def setNewPlayer(sid, data):
@sio.event
async def dice(sid, data):
    for x in range(8):
        if(entitiesList[x+8][0] == sid):
            temp = "k"+str(data)+" "+str(randrange(data)+1)
            await sio.emit("diceRolled", [x, temp])
            return

canvasBackup = ""

@sio.event
async def refresh(sid, d):
    await sio.emit('refreshCanvas', canvasBackup, sid)

@sio.event
async def canvas(sid, canvasItself):
    canvasBackup = canvasItself
    await sio.emit('refreshCanvas', canvasItself)


@sio.event
async def menacingRequest(sid, d):
    print("Mg sent menacing request")
    if(d == 0):
        await sio.emit("startMenacingEffect",0)
    else:
        await sio.emit("stopMenacingEffect",0)

app.router.add_get('/', index)
if __name__ == '__main__':
    web.run_app(app)
    for resource in app.router.resources():
        print(resource)
