#ifndef PROJECT_SERVERIMPL_H
#define PROJECT_SERVERIMPL_H

#include <iostream>
#include <memory>
#include <string>
#include <thread>

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>

#include "transport.pb.h"
#include "transport.grpc.pb.h"

using grpc::Server;
using grpc::ServerAsyncResponseWriter;
using grpc::ServerBuilder;
using grpc::ServerCompletionQueue;
using grpc::ServerContext;
using grpc::Status;

using jrtransport::ID;
using jrtransport::PingRequest;
using jrtransport::PongResponse;
using jrtransport::JRTransportService;


namespace JollyRoger {
namespace JRTransport {

class ServerImpl final {
  public:
    ServerImpl();
    ~ServerImpl();

    void Run();
    const unsigned long long RequestCount();

  private:
    class CallData {
      public:
        CallData(JRTransportService::AsyncService* service, ServerCompletionQueue* cq);
        void Proceed();

      private:
        JRTransportService::AsyncService* service_;

        ServerCompletionQueue* cq_;

        ServerContext ctx_;

        PingRequest pingRequest_;
        PongResponse pongResponse_;

        ServerAsyncResponseWriter<PongResponse> pongResponder_;

        enum CallStatus { CREATE, PROCESS, FINISH };
        CallStatus status_;
    };

    // This can be run in multiple thread if needed.
    void HandleRPCs();

    JRTransportService::AsyncService* service_;

    std::unique_ptr<ServerCompletionQueue> cq_;
    std::unique_ptr<Server> server_;

    unsigned long long requestsProcessed;
};
} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_SERVERIMPL_H
