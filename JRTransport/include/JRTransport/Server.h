#ifndef PROJECT_SERVERIMPL_H
#define PROJECT_SERVERIMPL_H

//#include <iostream>
//#include <memory>
//#include <string>
//#include <thread>
//
//#include <grpc/support/log.h>
//#include <grpcpp/grpcpp.h>
//
//#include "transport.pb.h"

#include <thread>
#include <vector>

#include "transport.grpc.pb.h"

namespace JollyRoger {
namespace JRTransport {

class Server final {
  public:
    Server();
    virtual ~Server();

    void Run();
    void JoinWorkers();
    void ServerWait();
    void Stop();

    const unsigned long long RequestCount();
    bool IsRunning();

    static const int SERVER_THREAD_COUNT = 4;

  private:
    // This can be run in multiple thread if needed.
    void HandleRPCs();

    jrtransport::JRTransportService::AsyncService service_;

    std::unique_ptr<grpc::ServerCompletionQueue> cq_;
    std::unique_ptr<grpc::Server> server_ptr_;

    std::atomic<unsigned long long> requests_processed;  // TODO: make it atomic

    std::vector<std::thread> workers;
    std::atomic_bool is_running;
};
} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_SERVERIMPL_H
