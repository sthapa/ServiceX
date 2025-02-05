# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from typing import Optional

import pkg_resources
from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from servicex.models import UserModel


class ServiceXResource(Resource):
    def __init__(self):
        """
        Initialize object
        """
        super().__init__()

    @classmethod
    def _generate_advertised_endpoint(cls, endpoint):
        return "http://" + current_app.config['ADVERTISED_HOSTNAME'] + "/" + endpoint

    @staticmethod
    @jwt_required(optional=True)
    def get_requesting_user() -> Optional[UserModel]:
        """
        :return: User who submitted request for resource.
        If auth is enabled, this cannot be None for JWT-protected resources
        which are decorated with @auth_required or @admin_required.
        """
        user = None
        if current_app.config.get('ENABLE_AUTH'):
            user = UserModel.find_by_sub(get_jwt_identity())
        return user

    @classmethod
    def _get_app_version(cls):
        """
        Examine installed packages to get the version number for the ServiceX App
        :return: The version number, or the string "develop" if servicex_app not installed
        """
        try:
            app_version = pkg_resources.get_distribution('servicex_app').version
            return app_version
        except pkg_resources.DistributionNotFound:
            return "develop"
