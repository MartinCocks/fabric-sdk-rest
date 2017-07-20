# Test Fabcar Sample
#
# Basic tests to confirm that REST calls into the Fabcar sample network work.


# Copyright 2017 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from sys import argv
from fabric_rest import FabricRest
import subprocess
import traceback
import base64

testsPassed = 0
testsFailed = 0

def test_first_channel_name():
    """Test to confirm that the first channel on the network has the default name of
    mychannel.
    """
    global testsFailed
    try:
        first_channel = restserver.get_channels()["channels"][0]["channel_id"]
        _equals(first_channel, "mychannel", "First channel name test")
    except subprocess.CalledProcessError as err:
        testsFailed += 1
        print "\n! test_first_channel_name : failed \n!    Stack Trace:\n"
        traceback.print_exc()


def test_car_color():
    global testsFailed
    try:
        """Test to confirm that the first car returned from a ledger query is the color blue."""
        car_color = restserver.query_ledger("mychannel", chaincode_id="fabcar",
                                            data=r'{"fcn":"queryAllCars","args":[]}')["queryResult"][0]["Record"]["colour"]
        _equals(car_color, "blue", "Car color test")
    except subprocess.CalledProcessError as err:
        testsFailed += 1
        print "\n! test_car_color : failed  \n!    Stack Trace:\n"
        traceback.print_exc()

def test_peer_chaincode_query():
    global testsFailed
    try:
        """Test to confirm that querying a peer for fabcar chaincode returns a result and querying for fab does not."""
        chaincode_name = restserver.query_chaincode("fabcar","%5B0%5D")["queryResult"][0]["name"]
        _equals(chaincode_name, "fabcar", "Peer chaincode query test")
    except subprocess.CalledProcessError as err:
        testsFailed += 1
        print "\n! test_peer_chaincode_query : failed \n!    Stack Trace:\n"
        traceback.print_exc()
    try:
        empty_result = restserver.query_chaincode("fab","%5B0%5D")["queryResult"][0]
        _equals(empty_result, {}, "Peer chaincode not found query test")
    except subprocess.CalledProcessError as err:
        testsFailed += 1
        print "\n! test_peer_chaincode_query - not found: failed \n!    Stack Trace:\n"
        traceback.print_exc()

def test_chaincode_install():
    """Test to confirm that installing chaincode on a peer works."""
    global testsFailed
    global testsPassed
    try:
        # install chaincode: id, path(in archive), archive as base64 string, version, peers
        archiveFile = open('input/installTest.tar.gz', 'rb')
        archiveInb64 = base64.b64encode(archiveFile.read())
        install_result = restserver.install_chaincode("marbles","marbles02/marbles_chaincode.go",archiveInb64,"1.0","%5B0%5D")["peerResponses"]
        #install_result = restserver.install_chaincode_file("marbles","marbles02/marbles_chaincode.go","1.0","%5B0%5D")["peerResponses"]
        # print install_result
        testsPassed += 1
    except (subprocess.CalledProcessError,IOError,TypeError,KeyError) as err:
        testsFailed += 1
        print "\n! test_chaincode_install: failed \n!    Stack Trace:\n"
        traceback.print_exc()



def _equals(a, b, test_name):
    """Confirm that values a and b are equal, printing text to the screen."""
    global testsPassed
    global testsFailed
    if a == b:
        testsPassed+=1
        print test_name + ": passed"
    else:
        testsFailed+=1
        print "! " + test_name + ": failed"


if __name__ == "__main__":
    if len(argv) > 1:
        hostname = argv[1]
        port = argv[2]
    else:
        hostname = "localhost"
        port = "3000"

    restserver = FabricRest(hostname, port)

    test_first_channel_name()
    test_car_color()
    test_peer_chaincode_query()

    # COMMENTED OUT as needs to sort output parsing and running a second time.
    #test_chaincode_install()

    print "\nSummary:\n   Passed:  " + str(testsPassed) + "\n   Failed:  " + str(testsFailed)
