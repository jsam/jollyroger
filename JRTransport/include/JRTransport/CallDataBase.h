#ifndef PROJECT_CALLDATABASE_H
#define PROJECT_CALLDATABASE_H

// Those includes are used in derived classes which are handling requests.
#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>
#include "transport.grpc.pb.h"

namespace JollyRoger {
namespace JRTransport {

// Class encompasing the state and logic needed to serve a request.
class CallDataBase {

  public:
    // Take in the "service" instance (in this case representing an asynchronous
    // server) and the completion queue "cq" used for asynchronous communication
    // with the gRPC runtime.
    CallDataBase(jrtransport::JRTransportService::AsyncService* service,
            grpc::ServerCompletionQueue* cq);

    virtual ~CallDataBase();

    bool Proceed();

  protected:
    virtual bool Process() = 0;

    // Producer-consumer queue
    grpc::ServerCompletionQueue* cq_;

    // Communication with the gRPC runtime for an asynchronous server
    jrtransport::JRTransportService::AsyncService* service_;

    static const bool RPC_SUCCESS = true;
    static const bool RPC_FAILED = false;
  private:

    // Tiny state machine
    enum CallStatus { PROCESS, FINISH };
    CallStatus status_;
};

} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_CALLDATABASE_H
