import os
import re
import asyncio
import subprocess
import edge_tts
import edge_tts.communicate

orig_escape = edge_tts.communicate.escape
def smart_escape(text):
    res = orig_escape(text)
    # unescape break tags
    res = re.sub(r'&lt;break\s+time=&quot;(\d+m?s)&quot;\s*/&gt;', r'<break time="\1" />', res)
    return res

edge_tts.communicate.escape = smart_escape

async def test():
    t = 'तुम रात को तीन बजे छत को घूरते हुए किस बात का हिसाब लगा रहे हो? <break time="1500ms" /> उस इंसान का?'
    comm = edge_tts.Communicate(t, 'hi-IN-MadhurNeural', rate='-5%', pitch='-3Hz')
    await comm.save('test_break_ok.mp3')
    print('Generated test_break_ok.mp3')

asyncio.run(test())
