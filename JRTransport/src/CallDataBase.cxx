#include "JRTransport/CallDataBase.h"

using JollyRoger::JRTransport::CallDataBase;

CallDataBase::CallDataBase(jrtransport::JRTransportService::AsyncService* service,
        grpc::ServerCompletionQueue* cq) : service_(service), cq_(cq), status_(PROCESS) {}

CallDataBase::~CallDataBase() = default;

void CallDataBase::Proceed()
{
    if (status_ == PROCESS) {
        status_ = FINISH;
        this->Process();
    }
    else {
        GPR_ASSERT(status_ == FINISH);
        delete this;
    }
}