from flask import Flask, jsonify, request
from upload_data import main

app=Flask(__name__)
@app.route("/",methods=['GET'])
def index():
    if request.method=='GET':
        
        ################################
        ####### Incluir código #########
        ################################
        
        return jsonify(json_data)
    else:
        return jsonify({'Error':"This is a GET API method"})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=9007)
