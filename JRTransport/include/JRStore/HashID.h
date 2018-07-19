#ifndef PROJECT_HASHID_H
#define PROJECT_HASHID_H

#include <bitset>

namespace JollyRoger {
namespace JRStore {
//
//    const int SEARCH_SPACE_SIZE = 160;
//

template<unsigned int size>
class HashID {

  public:
    using Hash=std::bitset<size>;
    enum CMP { CURRENT_GREATER = -1, EQUAL = 0, OTHER_GREATER = 1};

  private:
    void Next();
    bool At(int index) const;

    /*
     * returns: -1 if current object is greater
     *          0 if they are equal
     *          1 if the other hash is greater
     */
    int CmpAt(int index, const HashID& other_hash);


public:
    HashID();
    HashID(const std::string& from_str);
    HashID(const HashID& other_hash);
    HashID(const Hash& other_hash);
    ~HashID() = default;

    std::string ToString();
    void SetAt(int index, bool bit);
    int IsGreater(const HashID& other_hash);

    std::tuple<bool, bool> HalfSub(bool a, bool b) const;
    const HashID& Sub(const HashID &other_hash);

    const std::bitset<size> &get_hash() const;

private:
    std::bitset<size> _hash;
};
} // namespace JRStore
} // namespace JollyRoger

#endif // PROJECT_HASHID_H
