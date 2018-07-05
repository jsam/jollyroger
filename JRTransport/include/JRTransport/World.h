///
/// @file    World.h
/// @author  jsam <contact@justsam.io>
///

#ifndef PROJECT_TEMPLATE_A_HELLO_WORLD_H
#define PROJECT_TEMPLATE_A_HELLO_WORLD_H

/// @brief JollyRoger namespace provides all needed services for operational ring.
/// @author  	jsam <contact@justsam.io>
namespace JollyRoger {
namespace JRTransport {

/// @brief   Here you put a short description of the class
/// Extended documentation for this class.
/// @author 	jsam <contact@justsam.io>
class World {
  public:
    /// @brief   Greets the caller
    /// @author 	jsam <contact@justsam.io>
    /// @brief	Simple hello world
    void greet();

    /// @brief   Returns the value passed to it
    /// Longer description that is useless here.
    /// @author 	jsam <contact@justsam.io>
    /// @param n (In) input number.
    /// @return Returns the input number given.
    int returnsN(int n);
};

} // namespace JRTransport
} // namespace JollyRoger

#endif // PROJECT_TEMPLATE_A_HELLO_WORLD_H
