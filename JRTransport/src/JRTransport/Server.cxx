#include <future>
#include <thread>

#include <grpc/support/log.h>
#include <grpcpp/grpcpp.h>

#include "JRTransport/AuthCallData.h"
#include "JRTransport/PingCallData.h"
#include "JRTransport/Server.h"

namespace JollyRoger {
namespace JRTransport {

Server::Server() : requests_processed(0), is_running(false) {}

Server::~Server() = default;

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

void Server::JoinWorkers()
{
    if (workers.empty()) {
        std::cout << "no threads started\n";
        return;
    }

    for (auto& w : workers) {
        w.join();
    }
}

void Server::ServerWait() { server_ptr_->Wait(); }

void Server::Stop()
{
    is_running = false;

    server_ptr_->Shutdown();
    cq_->Shutdown();

    std::cout << "waiting for server workers to join\n";
    JoinWorkers();
};

const unsigned long long Server::RequestCount() { return requests_processed.load(); }

bool Server::IsRunning() {
    return is_running.load();
}

void Server::HandleRPCs()
{
    using JollyRoger::JRTransport::AuthCallData;
    using JollyRoger::JRTransport::CallDataBase;
    using JollyRoger::JRTransport::PingCallData;

    new PingCallData(&service_, cq_.get());
    new AuthCallData(&service_, cq_.get());

    void* tag; // event
    bool ok;

    while (true) {
        if (cq_->Next(&tag, &ok)) {
            if (!ok)
                continue;                               // read failed, try again

            if(static_cast<CallDataBase*>(tag)->Proceed()) // read successful, handle rpc
                requests_processed++;
        }
        else {
            // server has been shut down, kill the running worker thread
            return;
        }
    }
}

} // namespace JRTransport
} // namespace JollyRoger
