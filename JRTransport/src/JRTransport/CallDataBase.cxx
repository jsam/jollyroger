#include "JRTransport/CallDataBase.h"

using JollyRoger::JRTransport::CallDataBase;

CallDataBase::CallDataBase(jrtransport::JRTransportService::AsyncService* service,
        grpc::ServerCompletionQueue* cq) : service_(service), cq_(cq), status_(PROCESS) {}

CallDataBase::~CallDataBase() = default;

bool CallDataBase::Proceed()
{
    if (status_ == PROCESS) {
        status_ = FINISH;
        return this->Process();
    }
    else if (status_ == FINISH) {
        delete this;
    }
    return RPC_FAILED;
}