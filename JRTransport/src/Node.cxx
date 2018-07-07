#include <iostream>

#include <grpc++/grpc++.h>

#include <JRTransport/Client.h>
#include <JRTransport/Server.h>

#include "JRTransport/Node.h"

namespace JollyRoger {
namespace JRTransport {

Node::Node(const std::string& uri)
    : client_(grpc::CreateChannel(uri, grpc::InsecureChannelCredentials())) {}

void Node::Connect()
{
    server_.Run();
    /// \todo write client logic here. Start a client thread which will send ping periodically

    //JollyRoger::JRTransport::Client client(grpc::CreateChannel(":50051", grpc::InsecureChannelCredentials()));
    auto response = client_.Ping();
    std::cout << "Received: " << response.destination().infohash() << "\n";
}

void Node::Disconnect() {
    server_.Stop();
}

} // namespace JRTransport
} // namespace JollyRoger
