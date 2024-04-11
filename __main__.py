from Server import app
from pyngrok import ngrok

#public_link = ngrok.connect(5000)
#print(public_link)

app.run(host = '0.0.0.0')