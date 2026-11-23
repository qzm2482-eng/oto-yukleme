import ssl, os, sys, json, asyncio, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile=os.path.expanduser('~/.ccr/ca-bundle.crt'))
import edge_tts
async def go(v,t,o,rate):
    com=edge_tts.Communicate(t,v,rate=rate,boundary="WordBoundary"); words=[]
    with open(o,'wb') as f:
        async for ch in com.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': words.append((ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']))
    json.dump(words,open(o+'.json','w'))
asyncio.run(go(*sys.argv[1:5]))
