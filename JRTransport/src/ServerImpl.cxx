#include "JRTransport/ServerImpl.h"

namespace JollyRoger {
namespace JRTransport {

ServerImpl::ServerImpl() : requestsProcessed(0) {}

ServerImpl::~ServerImpl()
{
    if (server_ != nullptr)
        server_->Shutdown();
    if (cq_ != nullptr)
        cq_->Shutdown();
}

void ServerImpl::Run()
{
    std::string server_address("0.0.0.0:50051");

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(service_);

    cq_ = builder.AddCompletionQueue();

    server_ = builder.BuildAndStart();
    std::cout << "Server listening on" << server_address << "\n";

    HandleRPCs();
}

const unsigned long long ServerImpl::RequestCount() { return requestsProcessed; }

void ServerImpl::HandleRPCs()
{
    new CallData(service_, cq_.get());
    void* tag;
    bool ok;
    while (true) {
        GPR_ASSERT(cq_->Next(&tag, &ok));
        GPR_ASSERT(ok);
        static_cast<CallData*>(tag)->Proceed();
    }
}

ServerImpl::CallData::CallData(JRTransportService::AsyncService* service, ServerCompletionQueue* cq)
    : service_(service), cq_(cq), pongResponder_(&ctx_), status_(CREATE)
{
    Proceed();
}

void ServerImpl::CallData::Proceed() {
    if (status_ == CREATE) {
        status_ = PROCESS;
        service_->RequestPing(&ctx_, &pingRequest_, &pongResponder_, cq_, cq_, this);
        //service_->RequestAuth(&ctx_, &authRequest_, &pongResponder_, cq_, cq_, this);
    }
    else if (status_ == PROCESS) {
        new CallData(service_, cq_);

        //TODO: actual processing
        std::string prefix("pong");

        ID* id = new ID();
        id->set_address("0.0.0.0");
        id->set_port("50051");
        id->set_infohash("infohash");

        pongResponse_.set_allocated_destination(id);

        status_ = FINISH;
        pongResponder_.Finish(pongResponse_, Status::OK, this);
    }
    else {
        GPR_ASSERT(status_ == FINISH);
        delete this;
    }

}

} // namespace JRTransport
} // namespace JollyRoger
