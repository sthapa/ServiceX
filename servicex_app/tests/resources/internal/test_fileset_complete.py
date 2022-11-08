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
from servicex.models import TransformRequest
from servicex import LookupResultProcessor, TransformerManager
from tests.resource_test_base import ResourceTestBase


class TestFilesetComplete(ResourceTestBase):
    def test_put_fileset_complete(self, mocker):
        import servicex
        mock_transformer_manager = mocker.MagicMock(TransformerManager)
        mock_transformer_manager.shutdown_transformer_job = mocker.Mock()

        submitted_request = self._generate_transform_request()
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest,
            'lookup',
            return_value=submitted_request)

        mock_processor = mocker.MagicMock(LookupResultProcessor)
        mocker.patch.object(TransformRequest, "save_to_db")

        client = self._test_client(lookup_result_processor=mock_processor,
                                   transformation_manager=mock_transformer_manager)

        response = client.put('/servicex/internal/transformation/1234/complete',
                              json={
                                  'files': 17,
                                  'files-failed': 2,
                                  'total-events': 1024,
                                  'total-bytes': 2046,
                                  'elapsed-time': 42
                              })
        assert response.status_code == 200
        mock_transform_request_read.assert_called_with('1234')
        mock_processor.report_fileset_complete.assert_called_with(
            submitted_request,
            num_files=17,
            num_failed=2,
            total_events=1024,
            total_bytes=2046,
            did_lookup_time=42
        )
        mock_transformer_manager.shutdown_transformer_job.assert_not_called()

    def test_put_fileset_complete_empty_dataset(self, mocker):
        import servicex
        mock_transformer_manager = mocker.MagicMock(TransformerManager)
        mock_transformer_manager.shutdown_transformer_job = mocker.Mock()

        submitted_request = self._generate_transform_request()
        mock_transform_request_read = mocker.patch.object(
            servicex.models.TransformRequest,
            'lookup',
            return_value=submitted_request)

        mock_processor = mocker.MagicMock(LookupResultProcessor)
        mocker.patch.object(TransformRequest, "save_to_db")
        submitted_request.save_to_db = mocker.Mock()

        client = self._test_client(lookup_result_processor=mock_processor,
                                   transformation_manager=mock_transformer_manager)

        response = client.put('/servicex/internal/transformation/BR549/complete',
                              json={
                                  'files': 0,
                                  'files-failed': 0,
                                  'total-events': 0,
                                  'total-bytes': 0,
                                  'elapsed-time': 0
                              })
        assert response.status_code == 200
        mock_transform_request_read.assert_called_with('BR549')
        mock_processor.report_fileset_complete.assert_called_with(
            submitted_request,
            num_files=0,
            num_failed=0,
            total_events=0,
            total_bytes=0,
            did_lookup_time=0
        )

        assert submitted_request.status == 'Complete'
        mock_transformer_manager.shutdown_transformer_job.assert_called_with("BR549", "my-ws")
