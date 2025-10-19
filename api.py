from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import re

app = Flask(__name__)

# Configure your secret key here (change this to your own secret key)
VALID_SECRET_KEYS = ["urNigga", "@still_alivenow"]

def generate_netflix_login_link(NetflixId):
    """
    Generate Netflix direct login link using NetflixId cookie
    """
    url = "https://ios.prod.ftl.netflix.com/iosui/user/15.48"
    
    params = {
        "appVersion": "15.48.1",
        "config": '{"gamesInTrailersEnabled":"false","isTrailersEvidenceEnabled":"false","cdsMyListSortEnabled":"true","kidsBillboardEnabled":"true","addHorizontalBoxArtToVideoSummariesEnabled":"false","skOverlayTestEnabled":"false","homeFeedTestTVMovieListsEnabled":"false","baselineOnIpadEnabled":"true","trailersVideoIdLoggingFixEnabled":"true","postPlayPreviewsEnabled":"false","bypassContextualAssetsEnabled":"false","roarEnabled":"false","useSeason1AltLabelEnabled":"false","disableCDSSearchPaginationSectionKinds":["searchVideoCarousel"],"cdsSearchHorizontalPaginationEnabled":"true","searchPreQueryGamesEnabled":"true","kidsMyListEnabled":"true","billboardEnabled":"true","useCDSGalleryEnabled":"true","contentWarningEnabled":"true","videosInPopularGamesEnabled":"true","avifFormatEnabled":"false","sharksEnabled":"true"}',
        "device_type": "NFAPPL-02-",
        "esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
        "idiom": "phone",
        "iosVersion": "15.8.5",
        "isTablet": "false",
        "languages": "en-US",
        "locale": "en-US",
        "maxDeviceWidth": "375",
        "model": "saget",
        "modelType": "IPHONE8-1",
        "odpAware": "true",
        "path": '["account","token","default"]',
        "pathFormat": "graph",
        "pixelDensity": "2.0",
        "progressive": "false",
        "responseFormat": "json",
    }

    headers = {
        "User-Agent": "Argo/15.48.1 (iPhone; iOS 15.8.5; Scale/2.00)",
        "x-netflix.request.attempt": "1",
        "x-netflix.client.idiom": "phone",
        "x-netflix.request.client.user.guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
        "x-netflix.context.profile-guid": "A4CS633D7VCBPE2GPK2HL4EKOE",
        "x-netflix.request.routing": '{"path":"/nq/mobile/nqios/~15.48.0/user","control_tag":"iosui_argo"}',
        "x-netflix.context.app-version": "15.48.1",
        "x-netflix.argo.translated": "true",
        "x-netflix.context.form-factor": "phone",
        "x-netflix.context.sdk-version": "2012.4",
        "x-netflix.client.appversion": "15.48.1",
        "x-netflix.context.max-device-width": "375",
        "x-netflix.context.ab-tests": "",
        "x-netflix.tracing.cl.useractionid": "4DC655F2-9C3C-4343-8229-CA1B003C3053",
        "x-netflix.client.type": "argo",
        "x-netflix.client.ftl.esn": "NFAPPL-02-IPHONE8=1-PXA-02026U9VV5O8AUKEAEO8PUJETCGDD4PQRI9DEB3MDLEMD0EACM4CS78LMD334MN3MQ3NMJ8SU9O9MVGS6BJCURM1PH1MUTGDPF4S4200",
        "x-netflix.context.locales": "en-US",
        "x-netflix.context.top-level-uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
        "x-netflix.client.iosversion": "15.8.5",
        "accept-language": "en-US;q=1",
        "x-netflix.argo.abtests": "",
        "x-netflix.context.os-version": "15.8.5",
        "x-netflix.request.client.context": '{"appState":"foreground"}',
        "x-netflix.context.ui-flavor": "argo",
        "x-netflix.argo.nfnsm": "9",
        "x-netflix.context.pixel-density": "2.0",
        "x-netflix.request.toplevel.uuid": "90AFE39F-ADF1-4D8A-B33E-528730990FE3",
        "x-netflix.request.client.timezoneid": "Asia/Dhaka",
        "Cookie": f"NetflixId={NetflixId}",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"Netflix API returned status code: {response.status_code}",
                "response_text": response.text
            }
        
        data = json.loads(response.text)
        
        if "value" not in data or "account" not in data["value"]:
            return {
                "success": False,
                "error": "Invalid response format from Netflix API",
                "response_text": response.text
            }
            
        token_info = data["value"]["account"]["token"]["default"]
        token_value = token_info["token"]
        expires_ms = token_info["expires"]
        expires_time = datetime.fromtimestamp(expires_ms / 1000)

        login_url = f"https://netflix.com/account?nftoken={token_value}"
        
        return {
            "success": True,
            "token": token_value,
            "login_url": login_url,
            "expires": expires_time.isoformat(),
            "expires_timestamp": expires_ms,
            "message": "Netflix direct login link generated successfully"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse JSON response: {str(e)}",
            "response_text": response.text if 'response' in locals() else "No response"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

@app.route('/api/gen', methods=['GET'])
def generate_netflix_link():
    """
    API endpoint to generate Netflix direct login link
    Required parameters: netflix_id, secret_key
    """
    netflix_id = request.args.get('netflix_id')
    secret_key = request.args.get('secret_key')
    
    # Validate required parameters
    if not netflix_id or not secret_key:
        return jsonify({
            "success": False,
            "error": "Missing required parameters: netflix_id and secret_key are required"
        }), 400
    
    # Validate secret key
    if secret_key not in VALID_SECRET_KEYS:
        return jsonify({
            "success": False,
            "error": "Invalid secret key"
        }), 401
    
    # Validate NetflixId format (basic validation)
    if not netflix_id or len(netflix_id) < 10:
        return jsonify({
            "success": False,
            "error": "Invalid NetflixId format"
        }), 400
    
    # Generate the login link
    result = generate_netflix_login_link(netflix_id)
    
    # Add API info
    if result["success"]:
        result["api_info"] = {
            "developer": "still_alivenow",
            "version": "1.0",
            "description": "Netflix Direct Login Link Generator API"
        }
    
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Netflix Login Link Generator",
        "developer": "@still_alivenow",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """Home page with API documentation"""
    documentation = {
        "api_name": "Netflix Direct Login Link Generator",
        "developer": "still_alivenow",
        "endpoints": {
            "generate_link": {
                "url": "/api/gen",
                "method": "GET",
                "parameters": {
                    "netflix_id": "NetflixId cookie value (required)",
                    "secret_key": "Your secret key (required)"
                },
                "description": "Generates a direct login link for Netflix account"
            },
            "health_check": {
                "url": "/api/health",
                "method": "GET",
                "description": "Check API health status"
            }
        },
        "example_request": "/api/gen?netflix_id=YOUR_NETFLIX_ID&secret_key=YOUR_SECRET_KEY"
    }
    return jsonify(documentation)

if __name__ == '__main__':
    # Configuration
    DEBUG_MODE = True  # Set to False in production
    PORT = 5000
    HOST = '0.0.0.0'
    
    print("=" * 60)
    print("Netflix Direct Login Link Generator API")
    print("Developed by: still_alivenow")
    print("=" * 60)
    print(f"Server starting on http://{HOST}:{PORT}")
    print("Available endpoints:")
    print("  GET / - API documentation")
    print("  GET /api/health - Health check")
    print("  GET /api/gen - Generate login link")
    print("=" * 60)
    
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
