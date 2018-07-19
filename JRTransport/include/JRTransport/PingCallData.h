#ifndef PROJECT_PINGCALLDATA_H
#define PROJECT_PINGCALLDATA_H

#include "CallDataBase.h"

namespace JollyRoger {
namespace JRTransport {
class PingCallData : public CallDataBase {
  public:
    PingCallData(jrtransport::JRTransportService::AsyncService* service,
            grpc::ServerCompletionQueue* cq);

    ~PingCallData() override = default;

    bool Process() override;


  private:
    grpc::ServerContext ctx_;
    jrtransport::PingRequest request_;
    jrtransport::PongResponse response_;
    grpc::ServerAsyncResponseWriter<jrtransport::PongResponse> responder_;
};

} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_PINGCALLDATA_H
