#ifndef PROJECT_CLIENT_H
#define PROJECT_CLIENT_H

#include "transport.grpc.pb.h"

namespace JollyRoger {
namespace JRTransport {

class Client {

  public:
    explicit Client(std::shared_ptr<grpc::Channel> channel);

    jrtransport::PongResponse Ping();
    jrtransport::AuthResponse Auth(const std::string& secret);

    // TODO: implement all other needed RPC for DHT

  private:
    std::unique_ptr<jrtransport::JRTransportService::Stub> stub_;
};
} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_CLIENT_H
