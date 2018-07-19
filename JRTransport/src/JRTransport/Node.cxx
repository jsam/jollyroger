#include <iostream>

#include <grpc++/grpc++.h>

#include <JRTransport/Client.h>
#include <JRTransport/Server.h>

#include "JRTransport/Node.h"

namespace JollyRoger {
namespace JRTransport {

Node::Node(const std::string& uri) :
    server_(new Server()), client_(grpc::CreateChannel(uri, grpc::InsecureChannelCredentials())) {

}

Node::~Node() = default;

void Node::Connect()
{
    server_->Run();
    /// \todo write client logic here. Start a client thread which will send ping periodically

    JollyRoger::JRTransport::Client client(grpc::CreateChannel(":50051", grpc::InsecureChannelCredentials()));
    auto _request = new jrtransport::PingRequest();

    auto _id = new jrtransport::ID();
    _id->set_infohash("infohash:ping");
    _request->set_allocated_source(_id);

    auto response = client_.Ping(_request);
    std::cout << "Received: " << response->destination().infohash() << "\n";
}

void Node::Serve() {
    server_->ServerWait();
}

void Node::Disconnect() { server_->Stop(); }

} // namespace JRTransport
} // namespace JollyRoger
