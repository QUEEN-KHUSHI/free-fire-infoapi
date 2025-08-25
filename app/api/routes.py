from flask import jsonify, request, Blueprint, Response
import requests
import binascii
from datetime import datetime
import json
from app.core.jwt_token import get_jwt
from app.core.encrypt import Encrypt_ID, encrypt_api
from app.core.parser import get_available_room


routes = Blueprint("routes", __name__)


@routes.route("/api/player-info", methods=["GET"])
def get_player_info():
    try:
        player_id = request.args.get("id")
        if not player_id:
            return jsonify(
                {
                    "status": "error",
                    "message": "Player ID is required",
                    "credits": "nexxlokesh",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ), 400

        token = get_jwt()
        if not token:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to generate JWT token",
                    "credits": "nexxlokesh",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ), 500

        data = bytes.fromhex(encrypt_api(f"08{Encrypt_ID(player_id)}1007"))
        url = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
        headers = {
            "X-Unity-Version": "2018.4.11f1",
            "ReleaseVersion": "OB50",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-GA": "v1 1",
            "Authorization": f"Bearer {token}",
            "Content-Length": "16",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }

        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            hex_response = binascii.hexlify(response.content).decode("utf-8")
            json_result = get_available_room(hex_response)
            parsed_data = json.loads(json_result)

            try:
                # Basic Info first
                player_data = {
                    "playerInformation": {
                        "name": parsed_data["1"]["data"]["3"]["data"],
                        "uid": player_id,
                        "likes": parsed_data["1"]["data"]["21"]["data"],
                        "level": parsed_data["1"]["data"]["6"]["data"],
                        "server": parsed_data["1"]["data"]["5"]["data"],
                        "signature": parsed_data["9"]["data"]["9"]["data"],
                        "booyah_pass_level": parsed_data["1"]["data"]["18"]["data"],
                        "account_created": datetime.fromtimestamp(
                            parsed_data["1"]["data"]["44"]["data"]
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                }

                # Animal Info second
                try:
                    player_data["animal"] = {
                        "name": parsed_data["8"]["data"]["2"]["data"]
                    }
                except:
                    player_data["animal"] = None

                # Guild Info last
                try:
                    player_data["Guild"] = {
                        "guildName": parsed_data["6"]["data"]["2"]["data"],
                        "guildId": parsed_data["6"]["data"]["1"]["data"],
                        "guildLevel": parsed_data["6"]["data"]["4"]["data"],
                        "guildMembers": parsed_data["6"]["data"]["6"]["data"],
                        "guildLeader": {
                            "uid": parsed_data["6"]["data"]["3"]["data"],
                            "nickName": parsed_data["7"]["data"]["3"]["data"],
                            "playerLevel": parsed_data["7"]["data"]["6"]["data"],
                            "booyah_pass_level": parsed_data["7"]["data"]["18"]["data"],
                            "likes": parsed_data["7"]["data"]["21"]["data"],
                            "account_created": datetime.fromtimestamp(
                                parsed_data["7"]["data"]["44"]["data"]
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        },
                    }
                except:
                    player_data["Guild"] = None

               
                result = {
                    "data": player_data,
                    "credits": "nexxlokesh"
                }

                return Response(
                    json.dumps(result, indent=2, sort_keys=False),
                    mimetype="application/json"
                )

            except Exception as e:
                return jsonify(
                    {
                        "message": f"Failed to parse player information: {str(e)}",
                        "credits": "nexxlokesh"
                    }
                ), 500

        return jsonify(
            {
                "message": f"API request failed with status code: {response.status_code}",
                "credits": "nexxlokesh"
            }
        ), response.status_code

    except Exception as e:
        return jsonify(
            {
                "message": f"An unexpected error occurred: {str(e)}",
                "credits": "nexxlokesh"
            }
        ), 500
