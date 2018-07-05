#include "JRTransport/ServerImpl.h"

namespace JollyRoger {
namespace JRTransport {

ServerImpl::ServerImpl() : requestsProcessed(0) {}

ServerImpl::~ServerImpl() {
    if (server_ != nullptr)
        server_->Shutdown();
    if (cq_ != nullptr)
        cq_->Shutdown();
}

void ServerImpl::Run() {
    std::string server_address("0.0.0.0:50051");

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(service_);

    cq_ = builder.AddCompletionQueue();

    server_ = builder.BuildAndStart();
    std::cout << "Server listening on" << server_address << "\n";

    HandleRPCs();
}

const unsigned long long ServerImpl::RequestCount() {
    return requestsProcessed;
}

void ServerImpl::HandleRPCs() {

}

//class ServerImpl final {
//  public:
//    ServerImpl() {}
//
//    ~ServerImpl() {}
//
//    void Run() {}
//
//    const unsigned long long RequestCount() { return requestsProcessed; }
//
//  private:
//    class CallData {
//      public:
//        CallData(JRTransport::AsyncService* service, ServerCompletionQueue* cq) {}
//
//        void Proceed() {}
//
//      private:
//        JRTransportService::AsyncService* service_;
//
//        ServerCompletionQueue* cq_;
//
//        ServerContext ctx_;
//
//        PingRequest pingRequest_;
//        PongResponse pongResponse_;
//
//        ServerAsyncResponseWriter<PongResponse> pongResponder_;
//
//        enum CallStatus { CREATE, PROCESS, FINISH };
//        CallStatus status_;
//    };
//
//
//
//    std::unique_ptr<ServerCompletionQueue> cq_;
//    JRTransport::AsyncService service_;
//    std::unique_ptr<Server> server_;
//
//    unsigned long long requestsProcessed;
//};

} // namespace JRTransport
} // namespace JollyRoger
