#ifndef PROJECT_CLIENT_H
#define PROJECT_CLIENT_H

#include <future>
#include <thread>

#include "JRUtils/MPMCQueue.h"

#include "transport.grpc.pb.h"

namespace JollyRoger {
namespace JRTransport {

class Client {

  public:
    explicit Client(std::shared_ptr<grpc::Channel> channel);

    // TODO: implement all other needed RPC for DHT
    jrtransport::PongResponse* Ping(jrtransport::PingRequest*);
    jrtransport::AuthResponse* Auth(jrtransport::AuthRequest* request);

  private:
    // Producer-consumer queue we use to communicate asynchronously with the gRPC runtime.
    grpc::CompletionQueue _cq;

    std::unique_ptr<jrtransport::JRTransportService::Stub> stub_;
};

} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_CLIENT_H
