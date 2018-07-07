#include <thread>
#include <future>

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>

#include "JRTransport/AuthCallData.h"
#include "JRTransport/PingCallData.h"
#include "JRTransport/Server.h"

namespace JollyRoger {
namespace JRTransport {

Server::Server() : requests_processed(0), is_running(false) {}

Server::~Server()
{
    if (server_ptr_ != nullptr)
        server_ptr_->Shutdown();
    if (cq_ != nullptr)
        cq_->Shutdown();
}

void Server::Run()
{
    // TODO: implement proper shutdown mechanism
    std::string server_address("0.0.0.0:50051");

    grpc::ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service_);

    cq_ = builder.AddCompletionQueue();

    server_ptr_ = builder.BuildAndStart();
    std::cout << "Server listening on " << server_address << "\n";

    is_running = true;

    for (int i = 0; i < SERVER_THREAD_COUNT; ++i) {
        workers.emplace_back(std::thread(&Server::HandleRPCs, this));
    }

    std::cout << "Started server with " << SERVER_THREAD_COUNT << " threads."
              << "\n";
}

void Server::Wait()
{
    if (workers.empty()) {
        std::cout << "no threads started\n";
        return;
    }

    if (!is_running) {
       std::cout << "server is not running\n";
    }

    std::cout << "waiting for server to shutdown\n";
    server_ptr_->Wait();
}

void Server::Stop()
{
    is_running = false;
    server_ptr_->Shutdown();
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    cq_->Shutdown();
};



const unsigned long long Server::RequestCount() { return requests_processed; }

void Server::HandleRPCs()
{
    using JollyRoger::JRTransport::AuthCallData;
    using JollyRoger::JRTransport::CallDataBase;
    using JollyRoger::JRTransport::PingCallData;

    new PingCallData(&service_, cq_.get());
    new AuthCallData(&service_, cq_.get());

    void* tag; // event
    bool ok;

    do {
        GPR_ASSERT(cq_->Next(&tag, &ok));
        GPR_ASSERT(ok);
        static_cast<CallDataBase*>(tag)->Proceed();
        std::cout << "running: " << is_running << std::endl;
    } while (is_running);

    std::cout << "quiting event loop" << std::endl;
    //std::terminate();
}

} // namespace JRTransport
} // namespace JollyRoger
