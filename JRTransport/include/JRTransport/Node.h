///
/// @file    Node.h
/// @author  jsam <contact@justsam.io>
///

#ifndef PROJECT_NODE_H
#define PROJECT_NODE_H

#include <string>

#include "JRTransport/Server.h"
#include "JRTransport/Client.h"

#include "transport.grpc.pb.h"

/// @brief JollyRoger namespace provides all needed services for operational ring.
/// @author  	jsam <contact@justsam.io>
namespace JollyRoger {

/// @brief JRTransport namespace provides a service for handling necessary RPC's.
/// @author  	jsam <contact@justsam.io>
namespace JRTransport {

/// @brief   Here you put a short description of the class
/// Extended documentation for this class.
/// @author 	jsam <contact@justsam.io>
class Node {
  public:
    explicit Node(const std::string& uri);
    virtual ~Node() = default;

    void Connect();
    void Disconnect();

//    void Get(std::string key);
//    void Set(std::string key, std::vector<char> value);

private:
    JollyRoger::JRTransport::Server server_;
    JollyRoger::JRTransport::Client client_;
};

} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_NODE_H
