from aiohttp import web
import aiohttp
from string import Template
import json
import webrtcvad
from logging import debug, info

#Only used for record function
import datetime
import wave


HOSTNAME='sammachin.ngrok.io'
CLIP_MIN_MS = 200  # 200ms - the minimum audio clip that will be used
MAX_LENGTH = 10000  # Max length of a sound clip for processing in ms
SILENCE_MS = 400  # How many continuous ms of silence determine the end of a phrase

# Constants:
MS_PER_FRAME = 20  # Duration of a frame in ms
CLIP_MIN_FRAMES = CLIP_MIN_MS // MS_PER_FRAME
SILENCE = SILENCE_MS// MS_PER_FRAME


## Example Processor, writes audio clips to wav files
class WriteFile(object):
    def __init__(self, path):
        self.path = path
    def process(self, count, payload, cli):
        if count > CLIP_MIN_FRAMES:  # If the buffer is less than CLIP_MIN_MS, ignore it
            info('Processing {} frames from {}'.format(count, cli))
            fn = "{}rec-{}-{}.wav".format(self.path, cli, datetime.datetime.now().strftime("%Y%m%dT%H%M%S"))
            output = wave.open(fn, 'wb')
            output.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
            output.writeframes(payload)
            output.close()
            info('File written {}'.format(fn))
        else:
            info('Discarding {} frames'.format(str(count))) 

processor = WriteFile("./recordings/").process



class BufferedPipe(object):
    def __init__(self, max_frames, sink):
        """
        Create a buffer which will call the provided `sink` when full.
        It will call `sink` with the number of frames and the accumulated bytes when it reaches
        `max_buffer_size` frames.
        """
        self.sink = sink
        self.max_frames = max_frames
        self.count = 0
        self.payload = b''
    def append(self, data, cli):
        """ Add another data to the buffer. `data` should be a `bytes` object. """
        self.count += 1
        self.payload += data
        if self.count == self.max_frames:
            self.process(cli)
    def process(self, cli):
        """ Process and clear the buffer. """
        self.sink(self.count, self.payload, cli)
        self.count = 0
        self.payload = b''



# Parse Content-Type header into dict
def ctparse(data):
  resp = {}
  resp['type'] = data.split(';')[0].split('/')[0]
  resp['subtype'] = data.split(';')[0].split('/')[1]
  params =  data.split(';')[1:]
  for p in params:
    k,v = p.split('=')
    resp[k.strip()] = v
  return resp

routes = web.RouteTableDef()

@routes.get('/answer')
async def answer(request):
  data={}
  data['hostname'] = HOSTNAME
  data['callerid'] = request.rel_url.query['from']
  filein = open('ncco.json')
  src = Template(filein.read())
  filein.close()
  ncco = json.loads(src.substitute(data))
  return web.json_response(ncco)
    

    
@routes.get('/socket')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    vad = webrtcvad.Vad()
    vad.set_mode(1) # Level of sensitivity
    listening = True
    tick = SILENCE
    frame_buffer = BufferedPipe(MAX_LENGTH // MS_PER_FRAME, processor)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
          data = json.loads(msg.data)
          print(data)
          if data['event'] == 'websocket:connected':
            calldata = data
            contenttype = ctparse(data['content-type'])
        elif msg.type == aiohttp.WSMsgType.BINARY:
          if vad.is_speech(msg.data, int(contenttype['rate'])) and listening:
            debug("SPEECH from {}".format(data['callerid']))
            tick = SILENCE
            frame_buffer.append(msg.data, data['callerid'])
          else:
            debug("Silence from {} TICK: {}".format(data['callerid'], tick))
            tick -= 1
            if tick == 0:
              frame_buffer.process(data['callerid'])      
        elif msg.type == aiohttp.WSMsgType.ERROR:
          print('ws connection closed with exception %s' % ws.exception())
        elif msg.type == aiohttp.WSMsgType.CLOSE:
          print('websocket connection closed')
    return ws



app = web.Application()
app.add_routes(routes)
web.run_app(app)