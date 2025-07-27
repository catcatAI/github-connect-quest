import pytest
from src.game.main import Game
from unittest.mock import MagicMock

@pytest.fixture
def game():
    with pytest.MonkeyPatch.context() as m:
        m.setattr("src.game.angela.DialogueManager", MagicMock())
        yield Game()

@pytest.mark.timeout(5)
def test_asset_loading(game):
    assert 'images' in game.assets
    assert 'sprites' in game.assets
    assert 'backgrounds' in game.assets['images']
    assert 'portraits' in game.assets['images']
    assert 'characters' in game.assets['sprites']
    assert 'icons' in game.assets['sprites']
    # 'portraits' are images, not sprites
    assert 'portraits' not in game.assets['sprites']

@pytest.mark.timeout(5)
def test_specific_assets_loaded(game):
    assert 'station' in game.assets['images']['backgrounds']
    assert 'angela' in game.assets['images']['portraits']
    assert 'player' in game.assets['sprites']['characters']
    assert 'schoolbag' in game.assets['sprites']['icons']
