#    소개원실 HW1 테스트케이스 - (c) 2019 이동민
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime, timedelta, timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.fields import DateTimeField
from rest_framework.test import APITestCase
from rest_framework import status

# 간단한 테스트 케이스들입니다.
# 문제가 있으면 Github에 이슈를 남겨주세요.

class 여러가지테스트(APITestCase):
    User = get_user_model()

    base_time = datetime.now(timezone.utc).replace(
        minute = 0, second = 0, microsecond = 0
    )

    ids = ('t1', 't2')
    passwords = ('HomeworkTest1', 'HomeworkTest2')

    def setUp(self):
        self.users = (
            self.User.objects.create_user(
                username = self.ids[0],
                password = self.passwords[0]
            ),
            self.User.objects.create_user(
                username = self.ids[1],
                password = self.passwords[1]
            )
        )

    # Helper functions

    def client_login(self, no):
        self.user = self.users[no]
        return self.client.login(
            username = self.ids[no],
            password = self.passwords[no]
        )

    def get_time(self, t):
        return self.base_time + timedelta(hours = t)

    def check_time(self, iso, t):
        # Compare equality of iso 8601 formatted string and datetime
        self.assertEqual(DateTimeField().to_internal_value(iso), t)

    def meeting(self, since, til):
        # Assemble a meeting object
        return {
            'sinceWhen': self.get_time(since),
            'tilWhen': self.get_time(til)
        }

    # post/get/put/delete helpers
    def post_meeting(self, since, til):
        return self.client.post('/meetings/', self.meeting(since, til))

    def get_meeting(self, id):
        return self.client.get("/meetings/{0}/".format(id))

    def delete_meeting(self, id):
        return self.client.delete("/meetings/{0}/".format(id))

    def put_meeting(self, id, since, til):
        return self.client.put("/meetings/{0}/".format(id),
            self.meeting(since, til))


    def check_meeting_success(self, response, since, til, user_id):
        # Check whether post/put meeting succeeded
        self.assertTrue(status.is_success(response.status_code))
        # check response itself
        self.check_time(response.data['sinceWhen'], self.get_time(since))
        self.check_time(response.data['tilWhen'], self.get_time(til))
        self.assertEqual(response.data['user'], user_id)
        # check /meetings/id/
        response = self.get_meeting(response.data['id'])
        self.assertTrue(status.is_success(response.status_code))
        self.check_time(response.data['sinceWhen'], self.get_time(since))
        self.check_time(response.data['tilWhen'], self.get_time(til))
        self.assertEqual(response.data['user'], user_id)
        # check /meetings/
        all = self.client.get('/meetings/')
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn(response.data, all.data)

    def check_meeting_failure(self, response):
        # todo: better checking?
        self.assertTrue(status.is_client_error(response.status_code))

    def check_delete_success(self, response, id):
        self.assertTrue(status.is_success(response.status_code))
        response = self.get_meeting(id)
        self.assertTrue(status.is_client_error(response.status_code))
        response = self.client.get('/meetings/')
        for meeting in response.data:
            self.assertNotEqual(meeting['id'], id)

    def check_delete_failure(self, response, id):
        self.assertTrue(status.is_client_error(response.status_code))


    # Shorthand functions
    def post_expect_success(self, since, til):
        prev = self.client.get('/meetings/').data
        resp = self.post_meeting(since, til)
        self.check_meeting_success(resp, since, til, self.user.id)
        curr = self.client.get('/meetings/').data
        for meeting in prev:
            self.assertIn(meeting, curr)
        return resp

    def post_expect_failure(self, since, til):
        all = self.client.get('/meetings/')
        resp = self.post_meeting(since, til)
        self.check_meeting_failure(resp)
        self.assertEqual(all.data, self.client.get('/meetings/').data)
        return resp

    def put_expect_success(self, id, since, til):
        prev = self.client.get('/meetings/').data
        resp = self.put_meeting(id, since, til)
        self.check_meeting_success(resp, since, til, self.user.id)
        self.assertEqual(resp.data['id'], id)
        curr = self.client.get('/meetings/').data
        for meeting in prev:
            if meeting['id'] != id:
                self.assertIn(meeting, curr)
        return resp

    def put_expect_failure(self, id, since, til):
        all = self.client.get('/meetings/')
        resp = self.put_meeting(id, since, til)
        self.check_meeting_failure(resp)
        self.assertEqual(all.data, self.client.get('/meetings/').data)
        return resp

    def delete_expect_success(self, id):
        prev = self.client.get('/meetings/').data
        resp = self.delete_meeting(id)
        self.check_delete_success(resp, id)
        curr = self.client.get('/meetings/').data
        for meeting in prev:
            if meeting['id'] != id:
                self.assertIn(meeting, curr)
        return resp

    def delete_expect_failure(self, id):
        all = self.client.get('/meetings/')
        resp = self.delete_meeting(id)
        self.check_delete_failure(resp, id)
        self.assertEqual(all.data, self.client.get('/meetings/').data)
        return resp





    def test_empty(self):
        response = self.client.get('/meetings/')
        self.assertEqual(response.data, [])

    def test_post_auth(self):
        response = self.client.post('/meetings/', self.meeting(1, 2))
        self.assertTrue(status.is_client_error(response.status_code))

    def test_post_then_delete(self):
        login = self.client_login(0)
        response = self.post_expect_success(1, 2)
        self.delete_expect_success(response.data['id'])
        self.client.logout()
        self.test_empty()

    def test_overlap(self):
        # 겹치는 시간 처리
        login = self.client_login(0)

        response1 = self.post_expect_success(6, 8)

        # overlap
        self.post_expect_failure(5, 7)
        self.post_expect_failure(7, 9)
        self.post_expect_failure(5, 9)

        # wrong order
        self.post_expect_failure(2, 1)
        self.post_expect_failure(1, 1)

        response2 = self.post_expect_success(4, 6)
        response3 = self.post_expect_success(8, 9)
        response4 = self.post_expect_success(14, 16)

        self.delete_expect_success(response1.data['id'])

        response5 = self.post_expect_success(6, 8)

        # cleanup
        self.delete_expect_success(response2.data['id'])
        self.delete_expect_success(response3.data['id'])
        self.delete_expect_success(response4.data['id'])
        self.delete_expect_success(response5.data['id'])

        self.client.logout()
        self.test_empty()

    def test_detail_auth(self):
        # 다른 유저의 예약 권한
        login = self.client_login(0)
        post_id = self.post_expect_success(4, 7).data['id']
        self.client.logout()

        login = self.client_login(1)
        # cannot put/delete/get from other users
        self.put_expect_failure(post_id, 5, 8)
        self.delete_expect_failure(post_id)
        get = self.get_meeting(post_id)
        self.assertTrue(status.is_client_error(get.status_code))
        self.client.logout()

        # login as original user to cleanup
        login = self.client_login(0)
        self.delete_expect_success(post_id)
        self.client.logout()
        self.test_empty()

    def test_put_overlap(self):
        # 회의 수정 시 겹침
        login = self.client_login(0)
        resp1 = self.post_expect_success(1, 2)
        resp2 = self.post_expect_success(5, 6)
        resp3 = self.post_expect_success(8, 9)

        id = resp2.data['id']

        # overlap
        self.put_expect_failure(id, 1, 3)
        self.put_expect_failure(id, 7, 10)

        # wrong order
        self.put_expect_failure(id, 6, 5)
        self.put_expect_failure(id, 6, 6)

        self.put_expect_success(id, 3, 8)
        self.put_expect_success(id, 2, 7)
        self.put_expect_success(id, 5, 6)

        # cleanup
        self.delete_expect_success(id)
        self.delete_expect_success(resp1.data['id'])
        self.delete_expect_success(resp3.data['id'])

        self.client.logout()
        self.test_empty()

    def test_users(self):
        resp = [[], []]

        login = self.client_login(0)
        to_delete = self.post_expect_success(10, 11).data['id']
        resp[0] = [
            self.post_expect_success(1, 2),
            self.post_expect_success(3, 4),
            self.post_expect_success(5, 6)
        ]
        self.delete_expect_success(to_delete)
        self.client.logout()

        login = self.client_login(1)
        to_delete = self.post_expect_success(10, 11).data['id']
        resp[1] = [
            self.post_expect_success(2, 3),
            self.post_expect_success(4, 5),
            self.post_expect_success(6, 7)
        ]
        self.delete_expect_success(to_delete)
        self.client.logout()

        # Test /users/ - account for possible order differences
        all = self.client.get("/users/")
        self.assertEqual(len(all.data), 2)

        for userdat in all.data:
            for i in [0, 1]:
                if (userdat['id'] == self.users[i].id):
                    self.assertEqual(
                        userdat['username'],
                        self.users[i].username
                    )
                    self.assertSequenceEqual(
                        userdat['meetings'],
                        [x.data['id'] for x in resp[i]]
                    )

        # Test /users/id/
        # No need to be precise, most of the checking has already been done
        for i in [1, 2]:
            self.assertIn(
                self.client.get("/users/{0}/".format(i)).data,
                all.data
            )
        # Cleanup
        for i in [0, 1]:
            login = self.client_login(i)
            for r in resp[i]:
                self.delete_expect_success(r.data['id'])
            self.client.logout()

        self.test_empty()
        return
