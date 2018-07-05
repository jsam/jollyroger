///
/// @file    World.h
/// @author  jsam <contact@justsam.io>
///

#ifndef PROJECT_TEMPLATE_B_HELLO_WORLD_H
#define PROJECT_TEMPLATE_B_HELLO_WORLD_H

/// @brief    Here you put a short description of the namespace
/// Extended documentation for this namespace
/// @author  	jsam <contact@justsam.io>
namespace JollyRoger {
namespace ProjB {

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

} // namespace Hello
} // namespace ProjectTemplate

#endif // PROJECT_TEMPLATE_B_HELLO_WORLD_H
