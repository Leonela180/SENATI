from tests.conftest import register


def test_invitacion_dirigida_solo_acepta_correo_elegido(app, client, other_client):
    register(client, 'owner@demo.pe')
    team_id = client.post('/api/v1/teams', json={'name': 'Recuerdos'}).json['data']['id']
    response = client.post(f'/api/v1/teams/{team_id}/invitations', json={'email': 'persona@demo.pe', 'display_name': 'Persona invitada'})
    token = response.json['data']['link'].split('token=')[1]
    preview = other_client.post('/api/v1/invitations/preview', json={'token': token})
    assert preview.json['data']['email'] == 'persona@demo.pe'
    register(other_client, 'otro@demo.pe')
    assert other_client.post('/api/v1/invitations/accept', json={'token': token}).status_code == 403
    invited = app.test_client()
    register(invited, 'persona@demo.pe')
    assert invited.post('/api/v1/invitations/accept', json={'token': token}).status_code == 200
    assert client.post('/api/v1/invitations/preview', json={'token': token}).status_code == 404


def test_invitacion_rechaza_correo_invalido(client):
    register(client)
    team_id = client.post('/api/v1/teams', json={'name': 'Recuerdos'}).json['data']['id']
    assert client.post(f'/api/v1/teams/{team_id}/invitations', json={'email': 'invalido'}).status_code == 400
