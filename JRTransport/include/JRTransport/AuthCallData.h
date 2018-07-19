#ifndef PROJECT_AUTHCALLDATA_H
#define PROJECT_AUTHCALLDATA_H

#include "CallDataBase.h"

namespace JollyRoger {
namespace JRTransport {
class AuthCallData : public CallDataBase {
  public:
    AuthCallData(jrtransport::JRTransportService::AsyncService* service,
            grpc::ServerCompletionQueue* cq);

    ~AuthCallData() override = default;

    bool Process() override;

  private:
    grpc::ServerContext ctx_;
    jrtransport::AuthRequest request_;
    jrtransport::AuthResponse response_;
    grpc::ServerAsyncResponseWriter<jrtransport::AuthResponse> responder_;
};
} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_AUTHCALLDATA_H
