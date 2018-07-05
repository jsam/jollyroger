///
/// @file    World.cxx
/// @author  jsam <contact@justsam.io>
///

#include "ProjB/World.h"
#include "JRTransport/World.h"

#include <iostream>

namespace JollyRoger {
namespace ProjB {

void World::greet()
{
  std::cout << "ProjB world!!" << std::endl;

  JollyRoger::JRTransport::World JRTransportWorld;
  JRTransportWorld.greet();
}

int World::returnsN(int n)
{

  /// \todo This is how you can markup a todo in your code that will show up in the documentation of your project.
  /// \bug This is how you annotate a bug in your code.
  return n;
}

} // namespace ProjB
} // namespace ProjectTemplate
