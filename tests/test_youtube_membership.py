import os
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from core import youtube_membership
from core.member import MemberList


def ppatch(obj, *args, **kwargs):
    prefix = 'core.youtube_membership'
    return patch(f"{prefix}.{obj}", *args, **kwargs)


class TestYoutube(unittest.TestCase):
    def test_get_members_from_csv(self):
        # Dados fictícios para teste
        fake_data = [
            {
                'Membros': 'João Silva',
                'Link do perfil': 'https://www.youtube.com/channel/'
                                  'UC-CQ5189EZ4hRDxwHtD7Sog',
                'Nível atual': 'Compilador',
                'Tempo total no nível (meses)': 0.5,
                'Tempo total como assinante (meses)': 0.5,
                'Última atualização': 'Virou assinante',
                'Carimbo de data/hora da última atualização':
                    '2023-05-03T05:32:33.558-07:00'
            },
            {
                'Membros': 'Ana Maria Silva',
                'Link do perfil': 'https://www.youtube.com/channel/'
                                  'UC-CQ5189EZ4hRDxwHtD7Sog',
                'Nível atual': 'Compilador',
                'Tempo total no nível (meses)': 1,
                'Tempo total como assinante (meses)': 2,
                'Última atualização': 'Virou assinante',
                'Carimbo de data/hora da última atualização':
                    '2023-04-29T07:56:41.806-07:00'
            }
        ]

        # Cria um DataFrame pandas com os dados fictícios
        fake_members_df = pd.DataFrame(fake_data)

        # Utiliza MagicMock para simular o resultado do
        # core.youtube_membership.read_csv
        with patch('core.youtube_membership.read_csv',
                   MagicMock(return_value=fake_members_df)):
            members = youtube_membership.get_members_from_csv(
                'fake_file_path.csv')

        self.assertIsInstance(members, MemberList)

        self.assertEqual(len(members.members), 2)

    def test_get_membership_badge_image(self):
        test_cases = [
            (0, "new.png"),
            (0.5, "new.png"),
            (1, "1_month.png"),
            (1.5, "1_month.png"),
            (2, "2_months.png"),
            (5.5, "2_months.png"),
            (6, "6_months.png"),
            (11.5, "6_months.png"),
            (12, "12_months.png"),
            (23.5, "12_months.png"),
            (24, "24_months.png"),
            (35.5, "24_months.png"),
            (36, "36_months.png"),
            (47.5, "36_months.png"),
            (48, "48_months.png"),
            (50, "48_months.png")
        ]

        for months, expected_badge_file_name in test_cases:
            badge_image_path = youtube_membership.get_membership_badge_image(
                months)
            expected_badge_image_path = os.path.join('assets', 'badges',
                                                     expected_badge_file_name)

            self.assertEqual(badge_image_path, expected_badge_image_path)

    def test_rename_csv_columns(self):
        # Dados fictícios para teste
        fake_data = [
            {
                'Membros': 'João Silva',
                'Link do perfil': 'https://www.youtube.com/channel/'
                                  'UC-CQ5189EZ4hRDxwHtD7Sog',
                'Nível atual': 'Compilador',
                'Tempo total no nível (meses)': 0.5,
                'Tempo total como assinante (meses)': 0.5,
                'Última atualização': 'Virou assinante',
                'Carimbo de data/hora da última atualização':
                    '2023-05-03T05:32:33.558-07:00'
            }
        ]

        # Cria um DataFrame pandas com os dados fictícios
        fake_members_df = pd.DataFrame(fake_data)

        # Renomeia as colunas do DataFrame
        renamed_members_df = youtube_membership.rename_csv_columns(
            fake_members_df)

        # Verifica se as colunas do DataFrame resultado estão corretamente
        # renomeadas
        expected_columns = ['name', 'profile_url', 'membership_level',
                            'total_time_in_level', 'total_time_as_member',
                            'last_update', 'last_update_timestamp']
        self.assertListEqual(list(renamed_members_df.columns),
                             expected_columns)

        # Verifica se o resultado tem o mesmo número de linhas que os dados
        # fictícios
        self.assertEqual(len(renamed_members_df), len(fake_members_df))

    def test_get_user_photo_url(self):
        # Exemplo de URL do canal do YouTube
        test_data = 'https://youtube.com/channel/UCFuIUoyHB12qpYa8Jpxoxow'

        # Exemplo de resposta da API do YouTube para a URL da foto do perfil
        fake_photo_url = ('https://yt3.googleusercontent.com'
                          '/ytc/AGIKgqNYnWV_wrW9eSH1bz2akU2yUHBPXV9NE383_'
                          'YAsvA=s176-c-k-c0x00ffffff-no-rj')

        # Utiliza MagicMock para simular o resultado de fetch_channel_photo_url
        with patch('core.youtube_membership.fetch_channel_photo_url',
                   MagicMock(return_value=fake_photo_url)):
            photo_url = youtube_membership.get_user_photo_url(test_data)

        # Verifica se a URL da foto do perfil é a esperada
        self.assertEqual(photo_url, fake_photo_url)

    def test_get_user_photo_url_with_none(self):
        # Exemplo de URL do canal do YouTube
        test_data = 'https://youtube.com/invalid_path/for/testing'

        photo_url = youtube_membership.get_user_photo_url(test_data)
        self.assertIsNone(photo_url)

    @ppatch('requests')
    def test_fetch_channel_photo_url(self, mock_requests):
        mock_channel_id = MagicMock()
        mock_requests.get.return_value.json.return_value = MagicMock(
            __contains__=MagicMock(return_value=True))
        result = youtube_membership.fetch_channel_photo_url(mock_channel_id)

        mock_requests.get.assert_called_once()
        mock_response = mock_requests.get.return_value
        mock_response.json.assert_called_once()

        mock_snipped = mock_response.json.return_value['items'][0]['snippet']
        mock_url = mock_snipped['thumbnails']['default']['url']

        self.assertEqual(result, mock_url)

    @ppatch('requests')
    def test_fetch_channel_photo_url_with_none_result(self, mock_requests):
        mock_channel_id = MagicMock()
        mock_requests.get.return_value.json.return_value = MagicMock(
            __contains__=MagicMock(return_value=False))
        result = youtube_membership.fetch_channel_photo_url(mock_channel_id)

        self.assertIsNone(result)

    @ppatch('Image')
    @ppatch('requests')
    @ppatch('AsciiArt')
    def test_photo_url_to_ascii_art(self,
                                    mock_ascii_art,
                                    mock_requests,
                                    mock_image):
        mock_photo_url = MagicMock()
        result = youtube_membership.photo_url_to_ascii_art(mock_photo_url)

        mock_requests.get.assert_called_once_with(mock_photo_url,
                                                  stream=True,
                                                  timeout=5)
        mock_response = mock_requests.get.return_value
        mock_image.open.assert_called_once_with(mock_response.raw)
        mock_ascii_art.from_pillow_image.assert_called_once_with(
            mock_image.open.return_value)
        mock_photo_ascii_art = mock_ascii_art.from_pillow_image.return_value

        mock_photo_ascii_art.to_ascii.assert_called_once_with(columns=100,
                                                              char="#")

        self.assertEqual(result, mock_photo_ascii_art.to_ascii.return_value)

    def test_extract_channel_id(self):
        # Exemplos de URLs do canal do YouTube
        test_data = [
            {
                'input': 'https://www.youtube.com/channel/'
                         'UCZxr48h7_qEXuM1imy6NcCg/join',
                'expected_output': 'UCZxr48h7_qEXuM1imy6NcCg'
            },
            {
                'input': 'https://youtube.com/channel/'
                         'UCFuIUoyHB12qpYa8Jpxoxow',
                'expected_output': 'UCFuIUoyHB12qpYa8Jpxoxow'
            },
            {
                'input': 'https://www.youtube.com/channel/'
                         'UCw5sX8pDXdaBk8hOlRLyI0A/about',
                'expected_output': 'UCw5sX8pDXdaBk8hOlRLyI0A'
            }
        ]

        # Testa a função extract_channel_id para cada exemplo de dados
        for data in test_data:
            channel_id = youtube_membership.extract_channel_id(data['input'])
            self.assertEqual(channel_id, data['expected_output'])

    @ppatch('pd')
    def test_read_csv(self, mock_pd):
        mock_file_csv = 'fake_file_path.csv'
        result = youtube_membership.read_csv(mock_file_csv)

        mock_pd.read_csv.assert_called_once_with(mock_file_csv)
        self.assertEqual(result, mock_pd.read_csv.return_value)

    @ppatch('get_user_photo_url')
    @ppatch('photo_url_to_ascii_art')
    @ppatch('get_membership_badge_image')
    @ppatch('ExtraInfo')
    def test_get_extra_info(self,
                            mock_extra_info_cls,
                            mock_get_membership_badge_image,
                            mock_photo_url_to_ascii_art,
                            mock_get_user_photo_url):
        mock_member = MagicMock()
        result = youtube_membership.get_extra_info(mock_member)

        mock_get_user_photo_url.assert_called_once_with(
            mock_member.profile_url)
        mock_photo_url_to_ascii_art.assert_called_once_with(
            mock_get_user_photo_url.return_value)
        mock_get_membership_badge_image.assert_called_once_with(
            mock_member.total_time_as_member)

        mock_extra_info_cls.assert_called_once_with(
            mock_get_user_photo_url.return_value,
            mock_get_membership_badge_image.return_value,
            mock_photo_url_to_ascii_art.return_value)

        self.assertEqual(result, mock_extra_info_cls.return_value)
