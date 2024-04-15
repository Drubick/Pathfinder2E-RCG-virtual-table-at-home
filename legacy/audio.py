import requests
import base64
from datetime import datetime, timedelta
from pprint import pprint
import json
from spotipy import oauth2
import webbrowser
import time

class Spotify():
	
    # Make a request to the /authorize endpoint to get an authorization code

	def __init__(self, client_id, secret) -> None:
		SCOPE = 'streaming user-read-currently-playing user-modify-playback-state user-read-playback-state'
		CACHE = '.spotipyoauthcache'
		SPOTIPY_REDIRECT_URI = 'http://localhost:8080'

		self.sp_oauth = oauth2.SpotifyOAuth(client_id, secret, SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE)
		self.base_url = 'https://api.spotify.com/v1'
		self.secret = secret
		self.client_id = client_id
		self.token_info = None
		self.session = requests.Session()

		self.handle_token()

	def handle_token(self, attempt = 0):
		'''
			Get's the token from the caché and stores it. Where it to 
		'''

		# Gets token from cache and if neccessary, refreshes it.
		# Else the user is prompted to access the token
		# If the token couldn't be loaded from the chache, the user is given
		# an url and prompted to access it.
		# If the 

		if self.token_info:
			if self.sp_oauth._is_token_expired(self.token_info):
				self.token_info = self._refresh_access_token(self.token_info['refresh_token'])
			else:
				return
		else:
			token_info = self.sp_oauth.get_cached_token()
			if token_info:
				self.token_info = token_info
			else:
				if (attempt > 5):
					return -1
				attempt += 1
				print('Auth url = ', self.sp_oauth.get_authorize_url())
				time.sleep(5)
				if self.handle_token(attempt=attempt) == -1:
					return
				self.token = input('Please introduce access token:\n')
		self.session.headers = {
			'Authorization': f'Bearer {self.token_info["access_token"]}',
			'Content-Type': 'application/json'
		}

	def get_current_player_info(self):
		current_player_request = self.get('/me/player')
		if current_player_request.status_code not in [200, 204]:
			print(f'Error whilst querying player: {current_player_request.content}')
			return
		if current_player_request.status_code == 204:
			print('Can\'t play, no active spotify player (press play and stop on the computer)')
			return
		return current_player_request.json()

	def play(self, uri = None):
		if self.get_current_player_info():
			if uri: 
				response = self.put('/me/player/play', {
					"context_uri": uri
				})
			else:
				response = self.put('/me/player/play')
			if response.status_code != 204:
				print(f'Error playing: {response.content}')
				return False
			return True
		return False
	
	def pause(self, device_id = None):
		if device_id:
			response = self.put('/me/player/pause', {
				'device_id': device_id
			})
		else:
			response = self.put('/me/player/pause')
		if response.status_code not in [200, 204]:
			print(f'Error whilst querying player: {response.content}')
			return
	
	def next(self, device_id = None):
		if device_id:
			response = self.post('/me/player/next', {
				'device_id': device_id
			})
		else:
			response = self.post('/me/player/next')
		if response.status_code not in [200, 204]:
			print(f'Error whilst querying player: {response.content}')
			return
	
	def prev(self, device_id = None):
		if device_id:
			response = self.post('/me/player/previous', {
				'device_id': device_id
			})
		else:
			response = self.post('/me/player/previous')
		if response.status_code not in [200, 204]:
			print(f'Error whilst querying player: {response.content}')
			return
		
	def shuffle(self, doShuffle):
		doShuffle = 'true' if doShuffle else 'false'
		response = self.put(f'/me/player/shuffle?state={doShuffle}', {
			'state': doShuffle
		})
		pass

		
	def get(self, uri):
		self.handle_token() # Checks that the token is up to date

		request = self.session.get(f'{self.base_url}{uri}')
		return request
	
	def put(self, uri = None, data = None, url = None):
		self.handle_token()
	
		if not url:
			url = f'{self.base_url}{uri}'
	
		#Refresh token if needed
		request = self.session.put(url, data= json.dumps(data) if data else None)	
		return request
	
	def post(self, uri = None, data = None, url = None):
		self.handle_token()

		if not url:
			url = f'{self.base_url}{uri}'

		request = self.session.post(url, data= json.dumps(data) if data else None)	
		return request


if __name__ == '__main__':
	with open('config.json', 'r') as file:
		config = json.load(file)
	spotify = Spotify(config['client_id'], config['client_secret'])

	spotify.play(uri = 'spotify:playlist:24tuCCPFwHEMYmsUBEPStm')
	# orders = {
	# 	'play': spotify.play,
	# 	'pause': spotify.pause,
	# 	'next': spotify.next,
	# 	'previous': spotify.prev
	# }

	# print(f'Spotfy controller in console mode: please write one of the following instructions: {", ".join(orders)}')
	# while True:
	# 	order = input()
	# 	if (order in orders):
	# 		orders[order]()
	# 	elif order == 'exit':
	# 		break


