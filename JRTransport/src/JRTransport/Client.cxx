#include <grpc++/grpc++.h>
#include <grpc/support/log.h>

#include "JRTransport/Client.h"

namespace JollyRoger {
namespace JRTransport {

Client::Client(std::shared_ptr<grpc::Channel> channel)
    : stub_(jrtransport::JRTransportService::NewStub(std::dynamic_pointer_cast<grpc::ChannelInterface>(channel))), _cq()
{
}

jrtransport::AuthResponse* Client::Auth(jrtransport::AuthRequest* request) { return nullptr; }

jrtransport::PongResponse* Client::Ping(jrtransport::PingRequest* request)
{
    if (request == nullptr) {
        throw "request is nullptr";
    }

    // Container for the data which we expect from the server
    auto _response = new jrtransport::PongResponse();

    // Context for the client. Used to store additional information which client-server share.
    grpc::ClientContext _ctx;

    // Store for the status of the RPC upon completion.
    grpc::Status _status;

    // stub_->AsyncSayHello() perform the RPC call, returning an instance we
    // store in "rpc". Because we are using the asynchronous API, we need the
    // hold on to the "rpc" instance in order to get updates on the ongoing RPC.
    std::unique_ptr<grpc::ClientAsyncResponseReader<jrtransport::PongResponse>> rpc(
        stub_->AsyncPing(&_ctx, *request, &_cq));

    // Request that, upon completion of the RPC, "_response" be updated with the
    // server's response; "_status" with the indication of whether the operation
    // was successful. Tag the request with the integer 1.
    int request_id = (rand() % 1024) + 1;
    rpc->Finish(_response, &_status, (void*)request_id); // tag should be probably checked in the future

    void* got_tag = nullptr;
    bool ok = false;
    _cq.Next(&got_tag, &ok);
    //_cq.AsyncNext(&got_tag, &ok, std::chrono::system_clock::now() + std::chrono::milliseconds(20));
    if ((got_tag == (void*)request_id) && ok && _status.ok()) {
        return _response;
    }
    throw "rpc failed";

    // Verify that the result from "cq" corresponds, by its tag, our previous
    // request.
    // GPR_ASSERT(got_tag == (void*)1);
    // ... and that the request was completed successfully. Note that "ok"
    // corresponds solely to the request for updates introduced by Finish().
    // GPR_ASSERT(ok);

    // Act upon the status of the actual RPC.
    //    if (_status.ok()) {
    //        return _response;
    //    }
    //    else {
    //        throw "rpc failed";
    //    }
}

} // namespace JRTransport
} // namespace JollyRoger
