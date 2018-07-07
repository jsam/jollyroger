#include "JRTransport/AuthCallData.h"

using JollyRoger::JRTransport::AuthCallData;

AuthCallData::AuthCallData(jrtransport::JRTransportService::AsyncService *service,
        grpc::ServerCompletionQueue *cq) : responder_(&ctx_), CallDataBase(service, cq)
{
    service->RequestAuth(&ctx_, &request_, &responder_, cq, cq, this);
}

void AuthCallData::Process() {
    new AuthCallData(service_, cq_);

    auto id = new jrtransport::ID();
    id->set_address("0.0.0.0");
    id->set_port("50051");
    id->set_infohash("infohash:authReply");

    this->response_.set_allocated_destination(id);
    responder_.Finish(this->response_, grpc::Status::OK, this);

}