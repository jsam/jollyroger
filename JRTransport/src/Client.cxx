#include <grpc++/grpc++.h>
#include <grpc/support/log.h>

#include "JRTransport/Client.h"

namespace JollyRoger {
namespace JRTransport {

Client::Client(std::shared_ptr<grpc::Channel> channel)
    : stub_(jrtransport::JRTransportService::NewStub(std::dynamic_pointer_cast<grpc::ChannelInterface>(channel)))
{
}

jrtransport::PongResponse Client::Ping()
{
    jrtransport::PingRequest _request;

    jrtransport::ID* _id = new jrtransport::ID();
    _id->set_infohash("infohash:ping");

    _request.set_allocated_source(_id);

    // Container for the data which we expect from the server
    jrtransport::PongResponse _response;

    // Context for the client. Used to store additional information which client-server share.
    grpc::ClientContext _ctx;

    // Producer-consumer queue we use to communicate asynchronously with the gRPC runtime.
    grpc::CompletionQueue _cq;

    // Store for the status of the RPC upon completion.
    grpc::Status _status;

    // stub_->AsyncSayHello() perform the RPC call, returning an instance we
    // store in "rpc". Because we are using the asynchronous API, we need the
    // hold on to the "rpc" instance in order to get updates on the ongoig RPC.
    std::unique_ptr<grpc::ClientAsyncResponseReader<jrtransport::PongResponse> > rpc(
        stub_->AsyncPing(&_ctx, _request, &_cq));

    // Request that, upon completion of the RPC, "_response" be updated with the
    // server's response; "_status" with the indication of whether the operation
    // was successful. Tag the request with the integer 1.
    rpc->Finish(&_response, &_status, (void*)1);
    void* got_tag;
    bool ok = false;
    // Block until the next result is available in the completion queue "cq".
    _cq.Next(&got_tag, &ok);

    // Verify that the result from "cq" corresponds, by its tag, our previous
    // request.
    GPR_ASSERT(got_tag == (void*)1);
    // ... and that the request was completed successfully. Note that "ok"
    // corresponds solely to the request for updates introduced by Finish().
    GPR_ASSERT(ok);

    // Act upon the status of the actual RPC.
    if (_status.ok()) {
        return _response;
    }
    else {
        throw "rpc failed";
    }
}

jrtransport::AuthResponse Client::Auth(const std::string& secret) {
    jrtransport::AuthResponse _response;
    return _response;
}

} // namespace JRTransport
} // namespace JollyRoger
