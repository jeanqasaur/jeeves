# Binding to the SMT solver 'Z3'
# See also http://research.microsoft.com/en-us/um/redmond/projects/z3
#
# Written by Sascha Boehme.

import sys, os
from ctypes import *


_z3 = CDLL("PATH_TO_Z3_LIB")


class Z3:
  def __init__(self, config={}):
    conf = _z3.Z3_mk_config()
    for key in config:
      _z3.Z3_set_param_value(conf, str(key), str(config[key]))
    self.ctx = _z3.Z3_mk_context(conf)

  def __del__(self):
    _z3.Z3_del_context(self.ctx)

 

  def mk_int_symbol(self, int_val):
    return _z3.Z3_mk_int_symbol(self.ctx, int(int_val))

  def mk_string_symbol(self, string_val):
    return _z3.Z3_mk_string_symbol(self.ctx, str(string_val))

  def dest_symbol(self, symbol):
    if _z3.Z3_get_symbol_kind(self.ctx, symbol) == 0:
      return _z3.Z3_get_symbol_int(self.ctx, symbol)
    else:
      return _z3.Z3_get_symbol_string(self.ctx, symbol)

  def _as_symbol(self, name):
    if isinstance(name, Symbol): return name
    else: return self.mk_string_symbol(name)



  def is_eq_sort(self, sort1, sort2):
    return _z3.Z3_is_eq_sort(self.ctx, sort1, sort2)

  def mk_uninterpreted_sort(self, name):
    return _z3.Z3_mk_uninterpreted_sort(self.ctx, self._as_symbol(name))

  def mk_bool_sort(self): return _z3.Z3_mk_bool_sort(self.ctx)
  def mk_int_sort(self): return _z3.Z3_mk_int_sort(self.ctx)
  def mk_real_sort(self): return _z3.Z3_mk_real_sort(self.ctx)
  def mk_bv_sort(self, size): return _z3.Z3_mk_bv_sort(self.ctx, size)
  def mk_array_sort(self, domain_sort, range_sort):
    return _z3.Z3_mk_array_sort(self.ctx, domain_sort, range_sort)

  def mk_tuple_sort(self, name, fields):
    num_fields = len(fields)
    field_names = (Symbol * num_fields)()
    field_sorts = (Sort * num_fields)()
    for i in range(num_fields):
      field_names[i] = self._as_symbol(fields[i][0])
      field_sorts[i] = fields[i][1]
    mk_tuple_decl = FuncDecl(None)
    proj_decls = (FuncDecl * num_fields)()
    s = _z3.Z3_mk_tuple_sort(self.ctx, self._as_symbol(name), num_fields,
      field_names, field_sorts, byref(mk_tuple_decl), proj_decls)
    return (s, mk_tuple_decl, proj_decls)

  def mk_enumeration_sort(self, name, enums):
    n = len(enums)
    enum_names = (Symbol * n)()
    for i in range(n): enum_names[i] = self._as_symbol(enums[i])
    enum_consts = (FuncDecl * n)()
    enum_testers = (FuncDecl * n)()
    s = _z3.Z3_mk_enumeration_sort(self.ctx, self._as_symbol(name), n,
      enum_names, enum_consts, enum_testers)
    return (s, enum_consts, enum_testers)

  def mk_list_sort(self, name, elem_sort):
    nil_decl = FuncDecl(None)
    is_nil_decl = FuncDecl(None)
    cons_decl = FuncDecl(None)
    is_cons_decl = FuncDecl(None)
    head_decl = FuncDecl(None)
    tail_decl = FuncDecl(None)
    s = _z3.Z3_mk_list_sort(self.ctx, self._as_symbol(name), elem_sort,
      byref(nil_decl), byref(is_nil_decl), byref(cons_decl),
      byref(is_cons_decl), byref(head_decl), byref(tail_decl))
    return (s, nil_decl, is_nil_decl, cons_decl, is_cons_decl, head_decl,
      tail_decl)

  def mk_datatype(self, name, constructors):
    num_constr = len(constructors)
    constr = (Constructor * num_constr)()
    for i in range(num_constr): constr[i] = constructors[i]
    s = _z3.Z3_mk_datatype(self.ctx, self._as_symbol(name), num_constr, constr)
    cs = []
    for i in range(num_constr): cs.append(constr[i])
    return (s, cs)

  def mk_datatypes(self, datatypes):
    num_sorts = len(datatypes)
    sort_names = (Symbol * num_sorts)()
    sorts = (Sort * num_sorts)()
    constrs = (ConstructorList * num_sorts)()
    for i in range(num_sorts):
      sort_names[i] = self._as_symbol(datatypes[i][0])
      constrs[i] = datatypes[i][1]
    _z3.Z3_mk_datatypes(self.ctx, sort_names, sorts, constrs)
    ss = []
    cs = []
    for i in range(num_sorts):
      ss.append(sorts[i])
      cs.append(constrs[i])
    return (ss, cs)

  def mk_constructor(self, name, recognizer, fields):
    num_fields = len(fields)
    field_names = (Symbol * num_fields)()
    field_sorts = (Sort * num_fields)()
    sort_refs = (c_uint * num_fields)()
    for i in range(num_fields):
      field_names[i] = self._as_symbol(fields[i][0])
      field_sorts[i] = self._as_symbol(fields[i][1])
      sort_refs[i] = self._as_symbol(fields[i][2])
    return _z3.Z3_mk_constructor(self.ctx, self._as_symbol(name),
      self._as_symbol(recognizer), num_fields, field_names, field_sorts,
      sort_refs)

  def mk_constructor_list(self, constructors):
    num_constr = len(constructors)
    constr = (Constructor * num_constr)()
    for i in range(num_constr): constr[i] = constructors[i]
    return _z3.Z3_mk_constructor_list(self.ctx, num_constr, constr)

  def query_constructor(self, constructor, num_fields):
    constr_decl = FuncDecl(None)
    tester_decl = FuncDecl(None)
    accessors = (FuncDecl * num_fields)()
    _z3.Z3_query_constructor(self.ctx, constructor, num_fields,
      byref(constr_decl), byref(tester_decl), accessors)
    acs = []
    for i in range(num_fields): acs.append(accessors[i])
    return (constr_decl, tester_decl, acs)

  def del_constructor(self, constructor):
    _z3.Z3_del_constructor(self.ctx, constructor)

  def del_constructor_list(self, constructor_list):
    _z3.Z3_del_constructor_list(self.ctx, constructor_list)

  def get_sort_kind(self, sort):
    return _sort_kind_tab[_z3.Z3_get_sort_kind(self.ctx, sort)]

  def get_sort_name(self, sort):
    return _z3.Z3_get_sort_name(self.ctx, sort)

  def get_bv_sort_size(self, sort):
    return _z3.Z3_get_bv_sort_size(self.ctx, sort)

  def dest_array_sort(self, sort):
    return (self.get_array_sort_domain(sort), self.get_array_sort_range(sort))

  def get_array_sort_domain(self, sort):
    return _z3.Z3_get_array_sort_domain(self.ctx, sort)

  def get_array_sort_range(self, sort):
    return _z3.Z3_get_array_sort_range(self.ctx, sort)

  def dest_tuple_sort(self, sort):
    field_decls = []
    for i in range(self.get_tuple_sort_num_fields(sort)):
      field_decls.append(self.get_tuple_sort_field_decl(sort, i))
    return (self.get_sort_name(sort), self.get_tuple_sort_mk_decl(sort),
      field_decls)

  def get_tuple_sort_mk_decl(self, sort):
    return _z3.Z3_get_tuple_sort_mk_decl(self.ctx, sort)

  def get_tuple_sort_num_fields(self, sort):
    return _z3.Z3_get_tuple_sort_num_fields(self.ctx, sort)

  def get_tuple_sort_field_decl(self, sort, index):
    return _z3.Z3_get_tuple_sort_field_decl(self.ctx, sort, index)

  def dest_datatype(self, sort):
    datatype = []
    for i in range(self.get_datatype_sort_num_constructors(sort)):
      constr = self.get_datatype_sort_constructor(sort, i)
      recog = self.get_datatype_sort_recognizer(sort, i)
      accs = []
      for j in range(self.get_domain_size(constr)):
        accs.append(self.get_datatype_sort_constructor_accessor(sort, i, j))
      datatype.append((constr, recog, accs))
    return datatype

  def get_datatype_sort_num_constructor(self, sort):
    return _z3.Z3_get_datatype_sort_num_constructors(self.ctx, sort)

  def get_datatype_sort_constructor(self, sort, index):
    return _z3.Z3_get_datatype_sort_constructor(self.ctx, sort, index)

  def get_datatype_sort_recognizer(self, sort, index):
    return _z3.Z3_get_datatype_sort_recognizer(self.ctx, sort, index)

  def get_datatype_sort_constructor_accessor(self, sort, i, j):
    return _z3.Z3_get_datatype_sort_constructor_accessor(self.ctx, sort, i, j)



  def mk_func_decl(self, name, domain_sorts, range_sort):
    dom_size = len(domain_sorts)
    dom = (Sort * dom_size)()
    for i in range(dom_size): dom[i] = domain_sorts[i]
    return _z3.Z3_mk_func_decl(self.ctx, self._as_symbol(name), dom_size,
      dom, range_sort)

  def mk_fresh_func_decl(self, prefix, domain_sorts, range_sort):
    dom_size = len(domain_sorts)
    dom = (Sort * dom_size)()
    for i in range(dom_size): dom[i] = domain_sorts[i]
    return _z3.Z3_mk_fresh_func_decl(self.ctx, prefix, dom_size, dom,
      range_sort) 
  
  def mk_injective_function(self, name, domain_sorts, range_sort):
    dom_size = len(domain_sorts)
    dom = (Sort * dom_size)()
    for i in range(dom_size): dom[i] = domain_sorts[i]
    return _z3.Z3_mk_injective_function(self.ctx, self._as_symbol(name),
      dom_size, dom, range_sort) 

  def dest_func_decl(self, decl):
    kind = self.get_decl_kind(decl)
    name = self.get_decl_name(decl)
    dom = self.get_decl_domain(decl)
    rng = self.get_decl_range(decl)
    return (kind, name, dom, rng)

  def get_decl_kind(self, decl):
    return _decl_kind_tab[_z3.Z3_get_decl_kind(self.ctx, decl)]

  def get_decl_name(self, decl): return _z3.Z3_get_decl_name(self.ctx, decl)

  def get_decl_num_parameters(self, decl):
    return _z3.Z3_get_decl_num_parameter(self.ctx, decl)

  def get_decl_parameter_kind(self, decl, idx):
    return _parameter_kind_tab[_z3.Z3_get_decl_parameter_kind(self.ctx, decl,
      idx)]

  def get_decl_int_parameter(self, decl, idx):
    return _z3.Z3_get_decl_int_parameter(self.ctx, decl, idx)

  def get_decl_double_parameter(self, decl, idx):
    return _z3.Z3_get_decl_double_parameter(self.ctx, decl, idx)

  def get_decl_symbol_parameter(self, decl, idx):
    return _z3.Z3_get_decl_symbol_parameter(self.ctx, decl, idx)

  def get_decl_sort_parameter(self, decl, idx):
    return _z3.Z3_get_decl_sort_parameter(self.ctx, decl, idx)

  def get_decl_ast_parameter(self, decl, idx):
    return _z3.Z3_get_decl_ast_parameter(self.ctx, decl, idx)

  def get_decl_func_decl_parameter(self, decl, idx):
    return _z3.Z3_get_decl_func_decl_parameter(self.ctx, decl, idx)

  def get_decl_rational_parameter(self, decl, idx):
    return _z3.Z3_get_decl_rational_parameter(self.ctx, decl, idx)

  def get_decl_domain(self, decl):
    domain_sorts = []
    for i in range(self.get_domain_size(decl)):
      domain_sorts.append(self.get_domain(decl, i))
    return domain_sorts

  def get_domain_size(self, decl):
    return _z3.Z3_get_domain_size(self.ctx, decl)
 
  def get_domain(self, decl, index):
    return _z3.Z3_get_domain(self.ctx, decl, index)

  def get_decl_range(self, decl): return _z3.Z3_get_range(self.ctx, decl)



  def is_eq_ast(self, t1, t2): return _z3.Z3_is_eq_ast(self.ctx, t1, t2)

  def mk_app(self, fun, args):
    num_args = len(args)
    ts = (Ast * num_args)()
    for i in range(num_args): ts[i] = args[i]
    return _z3.Z3_mk_app(self.ctx, fun, num_args, ts)

  def intern_mk_nary(self, f, args):
    num_args = len(args)
    ts = (Ast * num_args)()
    for i in range(num_args): ts[i] = args[i]
    return f(self.ctx, num_args, ts)

  def mk_const(self, name, sort):
    return _z3.Z3_mk_const(self.ctx, self._as_symbol(name), sort)

  def mk_fresh_const(self, prefix, sort):
    return _z3.Z3_mk_fresh_const(self.ctx, prefix, sort)

  def mk_label(self, name, is_positive, t):
    return _z3.Z3_mk_label(self.ctx, self._as_symbol(name), is_positive, t)

  def mk_true(self): return _z3.Z3_mk_true(self.ctx)

  def mk_false(self): return _z3.Z3_mk_false(self.ctx)

  def mk_eq(self, t1, t2): return _z3.Z3_mk_eq(self.ctx, t1, t2)

  def mk_distinct(self, args):
    return self.intern_mk_nary(_z3.Z3_mk_distinct, args)

  def mk_not(self, t): return _z3.Z3_mk_not(self.ctx, t)

  def mk_ite(self, t1, t2, t3): return _z3.Z3_mk_ite(self.ctx, t1, t2, t3)

  def mk_iff(self, t1, t2): return _z3.Z3_mk_iff(self.ctx, t1, t2)

  def mk_implies(self, t1, t2): return _z3.Z3_mk_implies(self.ctx, t1, t2)

  def mk_xor(self, t1, t2): return _z3.Z3_mk_xor(self.ctx, t1, t2)

  def mk_and(self, args): return self.intern_mk_nary(_z3.Z3_mk_and, args)

  def mk_or(self, args): return self.intern_mk_nary(_z3.Z3_mk_or, args)

  def mk_add(self, args): return self.intern_mk_nary(_z3.Z3_mk_add, args)

  def mk_mul(self, args): return self.intern_mk_nary(_z3.Z3_mk_mul, args)

  def mk_sub(self, args): return self.intern_mk_nary(_z3.Z3_mk_sub, args)

  def mk_unary_minus(self, t): return _z3.Z3_mk_unary_minus(self.ctx, t)

  def mk_div(self, t1, t2): return _z3.Z3_mk_div(self.ctx, t1, t2)

  def mk_mod(self, t1, t2): return _z3.Z3_mk_mod(self.ctx, t1, t2)

  def mk_rem(self, t1, t2): return _z3.Z3_mk_rem(self.ctx, t1, t2)

  def mk_lt(self, t1, t2): return _z3.Z3_mk_lt(self.ctx, t1, t2)

  def mk_le(self, t1, t2): return _z3.Z3_mk_le(self.ctx, t1, t2)

  def mk_gt(self, t1, t2): return _z3.Z3_mk_gt(self.ctx, t1, t2)

  def mk_ge(self, t1, t2): return _z3.Z3_mk_ge(self.ctx, t1, t2)

  def mk_int2real(self, t): return _z3.Z3_mk_int2real(self.ctx, t)

  def mk_bvnot(self, t): return _z3.Z3_mk_bvnot(self.ctx, t)

  def mk_bvand(self, t1, t2): return _z3.Z3_mk_bvand(self.ctx, t1, t2)

  def mk_bvor(self, t1, t2): return _z3.Z3_mk_bvor(self.ctx, t1, t2)

  def mk_bvxor(self, t1, t2): return _z3.Z3_mk_bvxor(self.ctx, t1, t2)

  def mk_bvnand(self, t1, t2): return _z3.Z3_mk_bvnand(self.ctx, t1, t2)

  def mk_bvnor(self, t1, t2): return _z3.Z3_mk_bvnor(self.ctx, t1, t2)

  def mk_bvxnor(self, t1, t2): return _z3.Z3_mk_bvxnor(self.ctx, t1, t2)

  def mk_bvneg(self, t): return _z3.Z3_mk_bvneg(self.ctx, t)

  def mk_bvadd(self, t1, t2): return _z3.Z3_mk_bvadd(self.ctx, t1, t2)

  def mk_bvsub(self, t1, t2): return _z3.Z3_mk_bvsub(self.ctx, t1, t2)

  def mk_bvmul(self, t1, t2): return _z3.Z3_mk_bvmul(self.ctx, t1, t2)

  def mk_bvudiv(self, t1, t2): return _z3.Z3_mk_bvudiv(self.ctx, t1, t2)

  def mk_bvsdiv(self, t1, t2): return _z3.Z3_mk_bvsdiv(self.ctx, t1, t2)

  def mk_bvurem(self, t1, t2): return _z3.Z3_mk_bvurem(self.ctx, t1, t2)

  def mk_bvsrem(self, t1, t2): return _z3.Z3_mk_bvsrem(self.ctx, t1, t2)

  def mk_bvsmod(self, t1, t2): return _z3.Z3_mk_bvsmod(self.ctx, t1, t2)

  def mk_bvult(self, t1, t2): return _z3.Z3_mk_bvult(self.ctx, t1, t2)

  def mk_bvslt(self, t1, t2): return _z3.Z3_mk_bvslt(self.ctx, t1, t2)

  def mk_bvule(self, t1, t2): return _z3.Z3_mk_bvule(self.ctx, t1, t2)

  def mk_bvsle(self, t1, t2): return _z3.Z3_mk_bvsle(self.ctx, t1, t2)

  def mk_bvuge(self, t1, t2): return _z3.Z3_mk_bvuge(self.ctx, t1, t2)

  def mk_bvsge(self, t1, t2): return _z3.Z3_mk_bvsge(self.ctx, t1, t2)

  def mk_bvugt(self, t1, t2): return _z3.Z3_mk_bvugt(self.ctx, t1, t2)

  def mk_bvsgt(self, t1, t2): return _z3.Z3_mk_bvsgt(self.ctx, t1, t2)

  def mk_concat(self, t1, t2): return _z3.Z3_mk_concat(self.ctx, t1, t2)

  def mk_extract(self, high, low, t):
    return _z3.Z3_mk_extract(self.ctx, high, low, t)

  def mk_sign_ext(self, n, t): return _z3.Z3_mk_sign_ext(self.ctx, n, t)

  def mk_zero_ext(self, n, t): return _z3.Z3_mk_zero_ext(self.ctx, n, t)

  def mk_bvshl(self, t1, t2): return _z3.Z3_mk_bvshl(self.ctx, t1, t2)

  def mk_bvlshr(self, t1, t2): return _z3.Z3_mk_bvlshr(self.ctx, t1, t2)

  def mk_bvashr(self, t1, t2): return _z3.Z3_mk_bvashr(self.ctx, t1, t2)

  def mk_rotate_left(self, n, t): return _z3.Z3_mk_rotate_left(self.ctx, n, t)

  def mk_rotate_right(self, n, t):
    return _z3.Z3_mk_rotate_right(self.ctx, n, t)

  def mk_int2bv(self, size, t): return _z3.Z3_mk_int2bv(self.ctx, size, t)

  def mk_bv2int(self, t, is_signed):
    return _z3.Z3_mk_bv2int(self.ctx, t, is_signed)

  def mk_bvadd_no_overflow(self, t1, t2, is_signed):
    return _z3.Z3_mk_add_no_overflow(self.ctx, t1, t2, is_signed)

  def mk_bvadd_no_underflow(self, t1, t2):
    return _z3.Z3_mk_add_no_underflow(self.ctx, t1, t2)

  def mk_bvsub_no_overflow(self, t1, t2):
    return _z3.Z3_mk_bvsub_no_overflow(self.ctx, t1, t2)

  def mk_bvsub_no_underflow(self, t1, t2, is_signed):
    return _z3.Z3_mk_bvsub_no_underflow(self.ctx, t1, t2, is_signed)

  def mk_bvsdiv_no_overflow(self, t1, t2):
    return _z3.Z3_mk_bvsdiv_no_overflow(self.ctx, t1, t2)

  def mk_bvneg_no_overflow(self, t):
    return _z3.Z3_mk_neg_no_overflow(self.ctx, t)

  def mk_bvmul_no_overflow(self, t1, t2, is_signed):
    return _z3.Z3_mk_bvmul_no_overflow(self.ctx, t1, t2, is_signed)

  def mk_bvmul_no_underflow(self, t1, t2):
    return _z3.Z3_mk_bvmul_no_underflow(self.ctx, t1, t2)

  def mk_select(self, t1, t2): return _z3.Z3_mk_select(self.ctx, t1, t2)

  def mk_store(self, t1, t2, t3): return _z3.Z3_mk_store(self.ctx, t1, t2, t3)

  def mk_const_array(self, s, t): return _z3.Z3_mk_const_array(self.ctx, s, t)

  def mk_map(self, f, ts):
    num_args = len(ts)
    args = (Ast * num_args)()
    for i in range(num_args): args[i] = ts[i]
    return _z3.Z3_mk_map(self.ctx, f, num_args, args)

  def mk_array_default(self, t): return _z3.Z3_mk_array_default(self.ctx, t)

  def mk_numeral(self, n, sort): return _z3.Z3_mk_numeral(self.ctx, n, sort)

  def mk_real(self, num, den): return _z3.Z3_mk_real(self.ctx, num, den)

  def mk_int(self, n, sort): return _z3.Z3_mk_int(self.ctx, n, sort)

  def mk_unsigned_int(self, n, sort):
    return _z3.Z3_mk_unsigned_int(self.ctx, n, sort)

  def mk_int64(self, n, sort): return _z3.Z3_mk_int64(self.ctx, n, sort)

  def mk_unsigned_int64(self, n, sort):
    return _z3.Z3_mk_unsigned_int64(self.ctx, n, sort)

  def mk_pattern(self, terms):
    return self.intern_mk_nary(_z3.Z3_mk_pattern, terms)
    
  def mk_bound(self, index, sort):
    return _z3.Z3_mk_bound(self.ctx, index, sort)

  def mk_forall(self, weight, patterns, variables, body):
    num_pats = len(patterns)
    pats = (Pattern * num_pats)()
    for i in range(num_pats): pats[i] = patterns[i]
    num_vars = len(variables)
    var_sorts = (Sort * num_vars)()
    var_names = (Symbol * num_vars)()
    for i in range(num_vars):
      var_names[i] = self._as_symbol(variables[i][0])
      var_sorts[i] = variables[i][1]
    return _z3.Z3_mk_forall(self.ctx, weight, num_pats, pats, num_vars,
      var_sorts, var_names, body)

  def mk_exists(self, weight, patterns, variables, body):
    num_pats = len(patterns)
    pats = (Pattern * num_pats)()
    for i in range(num_pats): pats[i] = patterns[i]
    num_vars = len(variables)
    var_sorts = (Sort * num_vars)()
    var_names = (Symbol * num_vars)()
    for i in range(num_vars):
      var_names[i] = self._as_symbol(variables[i][0])
      var_sorts[i] = variables[i][1]
    return _z3.Z3_mk_exists(self.ctx, weight, num_pats, pats, num_vars,
      var_sorts, var_names, body)

  def mk_quantifier(self, is_forall, weight, patterns, variables, body):
    num_pats = len(patterns)
    pats = (Pattern * num_pats)()
    for i in range(num_pats): pats[i] = patterns[i]
    num_vars = len(variables)
    var_sorts = (Sort * num_vars)()
    var_names = (Symbol * num_vars)()
    for i in range(num_vars):
      var_names[i] = self._as_symbol(variables[i][0])
      var_sorts[i] = variables[i][1]
    return _z3.Z3_mk_quantifier(self.ctx, is_forall, weight, num_pats, pats,
      num_vars, var_sorts, var_names, body)

  def mk_forall_const(self, weight, consts, patterns, body):
    num_cs = len(consts)
    cs = (App * num_cs)()
    for i in range(num_cs): cs[i] = consts[i]
    num_pats = len(patterns)
    pats = (Pattern * num_pats)()
    for i in range(num_pats): pats[i] = patterns[i]
    return _z3.Z3_mk_forall_const(self.ctx, weight, num_cs, cs, num_pats, pats,
      body)
    
  def mk_exists_const(self, weight, consts, patterns, body):
    num_cs = len(consts)
    cs = (App * num_cs)()
    for i in range(num_cs): cs[i] = consts[i]
    num_pats = len(patterns)
    pats = (Pattern * num_pats)()
    for i in range(num_pats): pats[i] = patterns[i]
    return _z3.Z3_mk_exists_const(self.ctx, weight, num_cs, cs, num_pats, pats,
      body)

  def get_ast_kind(self, t):
    return _ast_kind_tab[_z3.Z3_get_ast_kind(self.ctx, t)]

  def get_sort(self, t): return _z3.Z3_get_sort(self.ctx, t)

  def dest_numeral(self, t):
    return (self.get_numeral_string(t), self.get_sort(t))

  def get_numeral_string(self, t):
    return _z3.Z3_get_numeral_string(self.ctx, t)

  def get_numeral_small(self, t):
    num = c_longlong(0)
    den = c_longlong(0)
    if _z3.Z3_get_numeral_small(self.ctx, t, byref(num), byref(den)):
      return (num.value, den.value)
    else: return None

  def get_numeral_int(self, t):
    n = c_int(0)
    if _z3.Z3_get_numeral_int(self.ctx, t, byref(n)): return n.value
    else: return None

  def get_numeral_uint(self, t):
    n = c_uint(0)
    if _z3.Z3_get_numeral_uint(self.ctx, t, byref(n)): return n.value
    else: return None

  def get_numeral_int64(self, t):
    n = c_longlong(0)
    if _z3.Z3_get_numeral_int64(self.ctx, t, byref(n)): return n.value
    else: return None

  def get_numeral_uint64(self, t):
    n = c_ulonglong(0)
    if _z3.Z3_get_numeral_uint64(self.ctx, t, byref(n)): return n.value
    else: return None

  def get_bool_value(self, t):
    return _lbool_tab[_z3.Z3_get_bool_value(self.ctx, t)]

  def dest_app_ast(self, t):
    return self.dest_app(self.to_app(t))

  def dest_app(self, app):
    return (self.get_app_decl(app), self.get_app_args(app))

  def get_app_decl(self, app): return _z3.Z3_get_app_decl(self.ctx, app)

  def get_app_args(self, app):
    args = []
    for i in range(self.get_app_num_args(app)):
      args.append(self.get_app_arg(app, i))
    return args

  def get_app_num_args(self, app):
    return _z3.Z3_get_app_num_args(self.ctx, app)

  def get_app_arg(self, app, index):
    return _z3.Z3_get_app_arg(self.ctx, app, index)

  def app_to_ast(self, app): return _z3.Z3_app_to_ast(self.ctx, app)

  def to_app(self, t): return _z3.Z3_to_app(self.ctx, t)

  def dest_variable(self, t):
    return (self.get_index_value(t,), self.get_sort(t))

  def get_index_value(self, t): return _z3.Z3_get_index_value(self.ctx, t)

  def dest_quantifier(self, t):
    return (self.is_quantifier_forall(t), self.get_quantifier_weight(t),
      self.get_quantifier_patterns(t), self.get_quantifier_bounds(t),
      self.get_quantifier_body(t))

  def is_quantifier_forall(self, t):
    return _z3.Z3_is_quantifier_forall(self.ctx, t)

  def get_quantifier_weight(self, t):
    return _z3.Z3_get_quantifier_weight(self.ctx, t)

  def get_quantifier_patterns(self, t):
    pats = []
    for i in range(self.get_quantifier_num_patterns(t)):
      pats.append(self.get_quantifier_pattern_ast(t, i))
    return pats

  def get_quantifier_num_patterns(self, t):
    return _z3.Z3_get_quantifier_num_patterns(self.ctx, t)

  def get_quantifier_pattern_ast(self, t, index):
    return _z3.Z3_get_quantifier_pattern_ast(self.ctx, t, index)

  def get_quantifier_bounds(self, t):
    bs = []
    for i in range(self.get_quantifier_num_bound(t)):
      bs.append((self.get_quantifier_bound_name(t, i),
        self.get_quantifier_bound_sort(t, i)))
    return bs

  def get_quantifier_num_bound(self, t):
    return _z3.Z3_get_quantifier_num_bound(self.ctx, t)

  def get_quantifier_bound_name(self, t, index):
    return _z3.Z3_get_quantifier_bound_name(self.ctx, t, index)

  def get_quantifier_bound_sort(self, t, index):
    return _z3.Z3_get_quantifier_bound_sort(self.ctx, t, index)

  def get_quantifier_body(self, t):
    return _z3.Z3_get_quantifier_body(self.ctx, t)

  def get_pattern_terms(self, pat):
    ts = []
    for i in range(self.get_pattern_num_terms(pat)):
      ts.append(self.get_pattern(self, pat, i))
    return ts

  def get_pattern_num_terms(self, pat):
    return _z3.Z3_get_pattern_num_terms(self.ctx, pat)

  def get_pattern(self, pat, index):
    return _z3.Z3_get_pattern(self.ctx, pat, index)



  def simplify(self, t): return _z3.Z3_simplify(self.ctx, t)



  def push(self): _z3.Z3_push(self.ctx)

  def pop(self, num_scopes): _z3.Z3_pop(self.ctx, num_scopes)

  def persist_ast(self, t, num_scopes):
    _z3.Z3_persist_ast(self.ctx, t, num_scopes)

  def assert_cnstr(self, t): _z3.Z3_assert_cnstr(self.ctx, t)

  def check(self): return _sat_tab[_z3.Z3_check(self.ctx)]

  def check_and_get_model(self):
    model = Model(None)
    r = _z3.Z3_check_and_get_model(self.ctx, byref(model))
    return (_sat_tab[r], model)

  def check_assumptions(self, assumptions, core):
    num_assms = len(assumptions)
    assms = (Ast * num_assms)()
    for i in range(num_assms): assms[i] = assumptions[i]
    model = Model(None)
    proof = Ast(None)
    core_size = c_uint(len(core))
    c = (Ast * num_assms)()
    for i in range(len(core)): c[i] = core[i]
    r = _z3.Z3_check_assumptions(self.ctx, num_assms, assms, byref(model),
      byref(proof), byref(core_size), c)
    cs = []
    for i in range(core_size.value): cs.append(c[i])
    return (_sat_tab[r], model, proof, cs)

  def soft_check_cancel(self): _z3.Z3_soft_check_cancel(self.ctx)

  def get_search_failure(self):
    return _search_failure_tab[_z3.Z3_get_search_failure(self.ctx)]

  def del_model(self, model): _z3.Z3_del_model(self.ctx, model)



  def get_relevant_labels(self): return _z3.Z3_get_relevant_labels(self.ctx)

  def get_relevant_literals(self):
    return _z3.Z3_get_relevant_literals(self.ctx)

  def get_guessed_literals(self): return _z3.Z3_get_guessed_literals(self.ctx)

  def del_literals(self, lits): _z3.Z3_del_literals(self.ctx, lits)

  def get_num_literals(self, lits):
    return _z3.Z3_get_num_literals(self.ctx, lits)

  def get_label_symbol(self, lits, index):
    return _z3.Z3_get_label_symbol(self.ctx, lits, index)

  def get_literal(self, lits, index):
    return _z3.Z3_get_literal(self.ctx, lits, index)

  def disable_literal(self, lits, index):
    _z3.Z3_disable_literal(self.ctx, lits, index)

  def block_literals(self, lits): _z3.Z3_block_literals(self.ctx, lits)



  def get_model_constants(self, model):
    cs = []
    for i in range(self.get_model_num_constants(model)):
      decl = self.get_model_constant(model, i)
      value = self.eval_func_decl(model, decl)
      cs.append((decl, value))
    return cs

  def get_model_num_constants(self, model):
    return _z3.Z3_get_model_num_constants(self.ctx, model)

  def get_model_constant(self, model, index):
    return _z3.Z3_get_model_constant(self.ctx, model, index)

  def eval_func_decl(self, model, decl):
    t = Ast(None)
    if _z3.Z3_eval_func_decl(self.ctx, model, decl, byref(t)): return t
    else: return None

  def get_model_funcs(self, model):
    fs = []
    for i in range(self.get_model_num_funcs(model)):
      decl = self.get_model_func_decl(model, i)
      vals = []
      for j in range(self.get_model_num_entries(model, i)):
        args = []
        for k in range(self.get_model_func_entry_num_args(model, i, j)):
          args.append(self.get_model_func_entry_arg(model, i, j, k))
        val = self.get_model_func_entry_value(model, i, j)
        vals.append((args, val))
      else_val = self.get_model_func_else(model, i)
      fs.append((decl, vals, else_val))
    return fs

  def get_model_num_funcs(self, model):
    return _z3.Z3_get_model_num_funcs(self.ctx, model)

  def get_model_func_decl(self, model, index):
    return _z3.Z3_get_model_func_decl(self.ctx, model, index)

  def get_model_func_num_entries(self, model, index):
    return _z3.Z3_get_model_func_num_entries(self.ctx, model, index)

  def get_model_func_entry_num_args(self, model, i, j):
    return _z3.Z3_get_model_func_entry_num_args(self.ctx, model, i, j)

  def get_model_func_entry_arg(self, model, i, j, k):
    return _z3.Z3_get_model_func_entry_arg(self.ctx, model, i, j, k)

  def get_model_func_entry_value(self, model, i, j):
    return _z3.Z3_get_model_func_entry_value(self.ctx, model, i, j)

  def get_model_func_else(self, model, index):
    return _z3.Z3_get_model_func_else(self.ctx, model, index)

  def get_as_array_value(self, t):
    num_entries = self.is_array_value(t)
    if num_entries == None: return None
    else: return self.get_array_value(t, num_entries)

  def is_array_value(self, t):
    num_entries = c_uint(0)
    if _z3.Z3_is_array_value(self.ctx, t, byref(num_entries)):
      return num_entries.value
    else: return None

  def get_array_value(self, t, num_entries):
    indices = (Ast * num_entries)()
    values = (Ast * num_entries)()
    for i in range(num_entries):
      indices[i] = Ast(None)
      values[i] = Ast(None)
    else_value = Ast(None)
    _z3.Z3_get_array_value(self.ctx, t, num_entries, indices, values,
      byref(else_value))
    vals = []
    for i in range(num_entries): vals.append((indices[i], values[i]))
    return (vals, else_value)

  def eval(self, model, t):
    s = Ast(None)
    if _z3.Z3_eval(self.ctx, model, t, byref(s)): return s
    else: return None



  def parse_smtlib_string(self, input, sort_dict={}, decl_dict={}):
    (num_sorts, sort_names, sorts) = self._get_sorts_from_dict(sort_dict)
    (num_decls, decl_names, decls) = self._get_decls_from_dict(decl_dict)
    _z3.Z3_parse_smtlib_string(self.ctx, c_char_p(input),
      c_uint(num_sorts), sort_names, sorts,
      c_uint(num_decls), decl_names, decls)
    
  def parse_smtlib_file(self, file_name, sort_dict={}, decl_dict={}):
    (num_sorts, sort_names, sorts) = self._get_sorts_from_dict(sort_dict)
    (num_decls, decl_names, decls) = self._get_decls_from_dict(decl_dict)
    _z3.Z3_parse_smtlib_file(self.ctx, c_char_p(file_name),
      c_uint(num_sorts), sort_names, sorts,
      c_uint(num_decls), decl_names, decls)

  def _get_sorts_from_dict(self, sort_dict):
    num_sorts = len(sort_dict)
    sort_names = (Symbol * num_sorts)()
    sorts = (Sort * num_sorts)()
    i = 0
    for name in sort_dict:
      sort_names[i] = self._as_symbol(name)
      sorts[i] = Sort.from_param(sort_dict[name])
      i += 1
    return (num_sorts, sort_names, sorts)
  
  def _get_decls_from_dict(self, decl_dict):
    num_decls = len(decl_dict)
    decl_names = (Symbol * num_decls)()
    decls = (FuncDecl * num_decls)()
    i = 0
    for name in decl_dict:
      decl_names[i] = self._as_symbol(name)
      decls[i] = FuncDecl.from_param(decl_dict[name])
      i += 1
    return (num_decls, decl_names, decls) 

  def get_smtlib_formulas(self):
    forms = []
    for i in range(self.get_smtlib_num_formulas()):
      form.append(self.get_smtlib_formula(i))
    return forms

  def get_smtlib_num_formulas(self):
    return _z3.Z3_get_smtlib_num_formulas(self.ctx)

  def get_smtlib_formula(self, index):
    return _z3.Z3_get_smtlib_formula(self.ctx, index)

  def get_smtlib_assumptions(self):
    assms = []
    for i in range(self.get_smtlib_num_assumptions()):
      assms.append(self.get_smtlib_assumption(i))
    return assms

  def get_smtlib_num_assumptions(self):
    return _z3.Z3_get_smtlib_num_assumptions(self.ctx)

  def get_smtlib_assumption(self, index):
    return _z3.Z3_get_smtlib_assumption(self.ctx, index)

  def get_smtlib_decls(self):
    decls = []
    for i in range(self.get_smtlib_num_decls()):
      decls.append(self.get_smtlib_decl(i))
    return decls

  def get_smtlib_num_decls(self):
    return _z3.Z3_get_smtlib_num_decls(self.ctx)

  def get_smtlib_decl(self, index):
    return _z3.Z3_get_smtlib_decl(self.ctx, index)


  def parse_z3_string(self, input):
    return _z3.Z3_parse_z3_string(self.ctx, input)

  def parse_z3_file(self, file_name):
    return _z3.Z3_parse_z3_file(self.ctx, file_name)


  def parse_simplify_string(self, input):
    parser_output = c_char_p(None)
    t = _z3.Z3_parse_simplify_string(self.ctx, input, byref(parser_output))
    return (t, parser_output)

  def parse_simplify_file(self, file_name):
    parser_output = c_char_p(None)
    t = _z3.Z3_parse_simplify_file(self.ctx, input, byref(parser_output))
    return (t, parser_output)



  def trace_to_file(self, trace_file):
    return _z3.Z3_trace_to_file(self.ctx, c_char_p(str(trace_file)))
  def trace_to_stderr(self): _z3.Z3_trace_to_stderr(self.ctx)
  def trace_to_stdout(self): _z3.Z3_trace_to_stdout(self.ctx)
  def trace_off(self): _z3.Z3_trace_off(self.ctx)

  def open_log(self, filename):
    _z3.Z3_open_log(self.ctx, c_char_p(str(filename)))
  def close_log(self): _z3.Z3_close_log(self.ctx)

  def set_ast_print_mode(self, as_smtlib):
    _z3.Z3_set_ast_print_mode(self.ctx, 0 if as_smtlib else 1)
  def context_to_string(self): return _z3.Z3_context_to_string(self.ctx)
  def sort_to_string(self, sort): return _z3.Z3_sort_to_string(self.ctx, sort)
  def func_decl_to_string(self, decl):
    return _z3.Z3_func_decl_to_string(self.ctx, decl)
  def ast_to_string(self, t): return _z3.Z3_ast_to_string(self.ctx, t)
  def pattern_to_string(self, pat):
    return _z3.Z3_pattern_to_string(self.ctx, pat)
  def model_to_string(self, model):
    return _z3.Z3_model_to_string(self.ctx, model)

  def benchmark_to_smtlib_string(self, name, logic, status, attributes,
    assumptions, formula):
      num_assms = len(assumptions)
      assms = (Ast * num_assms)()
      for i in range(num_assms): assms[i] = assumptions[i]
      return _z3.Z3_benchmark_to_smtlib_string(self.ctx, name, logic, status,
        attributes, num_assms, assms, formula)

  def get_context_assignment(self):
    return _z3.Z3_get_context_assignment(self.ctxt)


  def get_error_code(self):
    return _error_code_tab[_z3.Z3_get_error_code(self.ctx)]
  
  def set_error_handler(self, handler):
    _z3.Z3_set_error_handler(self.ctx, handler)

  def set_error(self, error_code):
    for i in _error_code_tab:
      if _error_code_tab[i] == error_code:
        _z3.Z3_set_error(self.ctx, i)
        return True
    return False
    

def get_error_message(error_code):
  code = -1
  for i in _error_code_tab:
    if _error_code_tab[i] == error_code:
      return c_char_p(_z3.Z3_get_error_message(c_int(i))).value
  raise IndexError("No error message available for error code '" +
    error_code + "'.")


def reset_memory(): _z3.Z3_reset_memory()


def get_version():
  major = c_uint()
  minor = c_uint()
  build_number = c_uint()
  revision_number = c_uint()
  _z3.Z3_get_version(byref(major), byref(minor), byref(build_number),
    byref(revision_number))
  return (major.value, minor.value, build_number.value, revision_number.value)



class Symbol(c_void_p):
  def __init__(self, symbol): self._as_parameter_ = symbol
  def from_param(obj): return obj

class Sort(c_void_p):
  def __init__(self, sort): self._as_parameter_ = sort
  def from_param(obj): return obj

class FuncDecl(c_void_p):
  def __init__(self, decl): self._as_parameter_ = decl
  def from_param(obj): return obj

class Ast(c_void_p):
  def __init__(self, ast): self._as_parameter_ = ast
  def from_param(obj): return obj

class App(c_void_p):
  def __init__(self, app): self._as_parameter_ = app
  def from_param(obj): return obj

class Pattern(c_void_p):
  def __init__(self, pattern): self._as_parameter_ = pattern
  def from_param(obj): return obj

class Model(c_void_p):
  def __init__(self, model): self._as_parameter_ = model
  def from_param(obj): return obj

class Literals(c_void_p):
  def __init__(self, literals): self._as_parameter_ = literals
  def from_param(obj): return obj

class Constructor(c_void_p):
  def __init__(self, constructor): self._as_parameter_ = constructor
  def from_param(obj): return obj

class ConstructorList(c_void_p):
  def __init__(self, constructor_list): self._as_parameter_ = constructor_list
  def from_param(obj): return obj



def _add_strings(tab, start, seq):
  for i in range(len(seq)):
    tab[start + i] = seq[i]

_lbool_tab = {}
_add_strings(_lbool_tab, -1, ["false", "undef", "true"])
lbool_values = _lbool_tab.values()
_sat_tab = {}
_add_strings(_sat_tab, -1,  ["unsat", "unknown", "sat"])
sat_values = _sat_tab.values()

_parameter_kind_tab = {}
_add_strings(_parameter_kind_tab, 0, ["int", "double", "rational", "symbol",
  "sort", "ast", "func_decl"])
parameter_kind_values = _parameter_kind_tab.values()

_sort_kind_tab = {}
_add_strings(_sort_kind_tab, 0, ["uninterpreted_sort", "bool_sort", "int_sort",
  "real_sort", "bv_sort", "array_sort", "datatype_sort"])
sort_kind_values = _sort_kind_tab.values()

_ast_kind_tab = {}
_add_strings(_ast_kind_tab, 0, ["numeral_ast", "app_ast", "var_ast",
  "quantifier_ast"])
ast_kind_values = _ast_kind_tab.values()


_builtin_logic = ["true", "false", "=", "distinct", "ite", "and", "or", "iff",
  "xor", "not", "implies", "~"]
_builtin_arith = ["<=", ">=", "<", ">", "+", "-", "~", "*", "/", "div", "rem",
  "mod", "int-to-real"]
_builtin_array = ["store", "select", "const-array", "array-map",
  "array-default", "set-union", "set-intersect", "set-difference",
  "set-complement", "set-subset"]
_builtin_bv = ["bnum", "bit1", "bit0", "bvneg", "bvadd",
  "bvsub", "bvmul",
  "bvsdiv", "bvudiv", "bvsrem", "bvurem", "bvsmod",
  "bvsdiv0", "bvudiv0", "bvsrem0", "bvurem0", "bvsmod0",
  "bvule", "bvsle", "bvuge", "bvsge", "bvult", "bvslt", "bvugt", "bvsgt",
  "bvand", "bvor", "bvnot", "bvxor", "bvnand", "bvnor", "bvxnor",
  "concat", "sign-ext", "zero-ext", "extract", "repeat",
  "bvredor", "bvredand", "bvcomp", "bvshl", "bvlshr", "bvashr",
  "rotate-left", "rotate-right", "int2bv", "bv2int"]
_proof = ["pr-undef", "prop-true", "asserted", "goal", "mp",
  "refl", "symm", "trans", "trans*", "monotonicity", "quant-intro",
  "distributivity", "and-elim", "not-or-elim", "rewrite", "rewrite*",
  "pull-quant", "pull-quant*", "push-quant", "elim-unused-vars", "der",
  "quant-inst", "hypothesis", "lemma", "unit-resolution", "iff-true",
  "iff-false", "commutativity", "def-axiom", "def-intro", "apply-def",
  "iff~", "nnf-pos", "nnf-neg", "nnf*", "cnf*", "sk", "mp~", "th-lemma"]

_builtin = _builtin_logic + _builtin_arith + _builtin_array + _builtin_bv
def is_builtin(name): return name in _builtin
def is_proof(name): return name in _proof

_decl_kind_tab = {}
_add_strings(_decl_kind_tab, 256, _builtin_logic)
_add_strings(_decl_kind_tab, 512, ["anum"] + _builtin_arith)
_add_strings(_decl_kind_tab, 768, _builtin_array)
_add_strings(_decl_kind_tab, 1024, _builtin_bv)
_add_strings(_decl_kind_tab, 1280, _proof + ["uninterpreted"])
decl_kind_values = _decl_kind_tab.values()

_search_failure_tab = {}
_add_strings(_search_failure_tab, 0, ["no failure", "unknown", "timeout",
  "memout_watermark", "canceled", "num_conflicts", "theory", "quantifier"])
search_failure_values = _search_failure_tab.values()

_error_code_tab = {}
_add_strings(_error_code_tab, 0, ["ok", "sort error", "index out of bounds",
  "invalid arg", "parser error", "no parser", "invalid pattern", "memout fail"])
error_code_values = _error_code_tab.values()

_ast_print_mode_tab = {}
_add_strings(_ast_print_mode_tab, 0, ["smtlib", "low_level"])
ast_print_mode_balues = _ast_print_mode_tab.values()


def _z3_fun_void(f, argtypes):
  f.argtypes = argtypes

def _z3_fun(restype, f, argtypes):
  f.argtypes = argtypes
  f.restype = restype

_z3_fun(Symbol, _z3.Z3_mk_int_symbol, [c_void_p, c_int])
_z3_fun(Symbol, _z3.Z3_mk_string_symbol, [c_void_p, c_char_p])
_z3_fun(c_int, _z3.Z3_get_symbol_kind, [c_void_p, Symbol])
_z3_fun(c_int, _z3.Z3_get_symbol_int, [c_void_p, Symbol])
_z3_fun(c_char_p, _z3.Z3_get_symbol_string, [c_void_p, Symbol])

_z3_fun(c_int, _z3.Z3_is_eq_sort, [c_void_p, Sort, Sort])
_z3_fun(Sort, _z3.Z3_mk_uninterpreted_sort, [c_void_p, Symbol])
_z3_fun(Sort, _z3.Z3_mk_bool_sort, [c_void_p])
_z3_fun(Sort, _z3.Z3_mk_int_sort, [c_void_p])
_z3_fun(Sort, _z3.Z3_mk_real_sort, [c_void_p])
_z3_fun(Sort, _z3.Z3_mk_bv_sort, [c_void_p, c_uint])
_z3_fun(Sort, _z3.Z3_mk_array_sort, [c_void_p, Sort, Sort])
_z3_fun(Sort, _z3.Z3_mk_tuple_sort, [c_void_p, Symbol, c_uint,
  POINTER(Symbol), POINTER(Sort), POINTER(FuncDecl), POINTER(FuncDecl)])
_z3_fun(Sort, _z3.Z3_mk_enumeration_sort, [c_void_p, Symbol, c_uint,
  POINTER(Symbol), POINTER(FuncDecl), POINTER(FuncDecl)])
_z3_fun(Sort, _z3.Z3_mk_list_sort, [c_void_p, Symbol, Sort, POINTER(FuncDecl),
  POINTER(FuncDecl), POINTER(FuncDecl), POINTER(FuncDecl), POINTER(FuncDecl),
  POINTER(FuncDecl)])
_z3_fun(Constructor, _z3.Z3_mk_constructor, [c_void_p, Symbol, Symbol, c_uint,
  POINTER(Symbol), POINTER(Sort), POINTER(c_uint)])
_z3_fun(Sort, _z3.Z3_mk_datatype, [c_void_p, Symbol, c_uint,
  POINTER(Constructor)])
_z3_fun(ConstructorList, _z3.Z3_mk_constructor_list, [c_void_p, c_uint,
  POINTER(Constructor)])
_z3_fun_void(_z3.Z3_mk_datatypes, [c_void_p, c_uint, POINTER(Symbol),
  POINTER(Sort), POINTER(ConstructorList)])

_z3_fun_void(_z3.Z3_query_constructor, [c_void_p, Constructor, c_uint,
  POINTER(FuncDecl), POINTER(FuncDecl), POINTER(FuncDecl)])
_z3_fun_void(_z3.Z3_del_constructor, [c_void_p, Constructor])
_z3_fun_void(_z3.Z3_del_constructor_list, [c_void_p, ConstructorList])

_z3_fun(c_int, _z3.Z3_get_sort_kind, [c_void_p, Sort])
_z3_fun(Symbol, _z3.Z3_get_sort_name, [c_void_p, Sort])
_z3_fun(c_uint, _z3.Z3_get_bv_sort_size, [c_void_p, Sort])
_z3_fun(Sort, _z3.Z3_get_array_sort_domain, [c_void_p, Sort])
_z3_fun(Sort, _z3.Z3_get_array_sort_range, [c_void_p, Sort])
_z3_fun(FuncDecl, _z3.Z3_get_tuple_sort_mk_decl, [c_void_p, Sort])
_z3_fun(c_uint, _z3.Z3_get_tuple_sort_num_fields, [c_void_p, Sort])
_z3_fun(FuncDecl, _z3.Z3_get_tuple_sort_field_decl, [c_void_p, Sort, c_uint])
_z3_fun(c_uint, _z3.Z3_get_datatype_sort_num_constructors, [c_void_p, Sort])
_z3_fun(FuncDecl, _z3.Z3_get_datatype_sort_constructor, [c_void_p, Sort,
  c_uint])
_z3_fun(FuncDecl, _z3.Z3_get_datatype_sort_recognizer, [c_void_p, Sort,
  c_uint])
_z3_fun(FuncDecl, _z3.Z3_get_datatype_sort_constructor_accessor, [c_void_p,
  Sort, c_uint, c_uint])

_z3_fun(FuncDecl, _z3.Z3_mk_func_decl, [c_void_p, Symbol, c_uint,
  POINTER(Sort), Sort])
_z3_fun(FuncDecl, _z3.Z3_mk_fresh_func_decl, [c_void_p, c_char_p, c_uint,
  POINTER(Sort), Sort])
_z3_fun(FuncDecl, _z3.Z3_mk_injective_function, [c_void_p, Symbol, c_uint,
  POINTER(Sort), Sort])
_z3_fun(c_int, _z3.Z3_get_decl_kind, [c_void_p, FuncDecl])
_z3_fun(Symbol, _z3.Z3_get_decl_name, [c_void_p, FuncDecl])
_z3_fun(c_uint, _z3.Z3_get_decl_num_parameters, [c_void_p, FuncDecl])
_z3_fun(c_int, _z3.Z3_get_decl_parameter_kind, [c_void_p, FuncDecl, c_uint])
_z3_fun(c_int, _z3.Z3_get_decl_int_parameter, [c_void_p, FuncDecl, c_uint])
_z3_fun(c_double, _z3.Z3_get_decl_double_parameter, [c_void_p, FuncDecl,
  c_uint])
_z3_fun(Symbol, _z3.Z3_get_decl_symbol_parameter, [c_void_p, FuncDecl,
  c_uint])
_z3_fun(Sort, _z3.Z3_get_decl_sort_parameter, [c_void_p, FuncDecl, c_uint])
_z3_fun(Ast, _z3.Z3_get_decl_ast_parameter, [c_void_p, FuncDecl, c_uint])
_z3_fun(FuncDecl, _z3.Z3_get_decl_func_decl_parameter, [c_void_p, FuncDecl,
  c_uint])
_z3_fun(c_char_p, _z3.Z3_get_decl_rational_parameter, [c_void_p, FuncDecl,
  c_uint])
_z3_fun(c_uint, _z3.Z3_get_domain_size, [c_void_p, FuncDecl])
_z3_fun(Sort, _z3.Z3_get_domain, [c_void_p, FuncDecl, c_uint])
_z3_fun(Sort, _z3.Z3_get_range, [c_void_p, FuncDecl])

_z3_fun(c_int, _z3.Z3_is_eq_ast, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_app, [c_void_p, FuncDecl, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_const, [c_void_p, Symbol, Sort])
_z3_fun(Ast, _z3.Z3_mk_fresh_const, [c_void_p, c_char_p, Sort])
_z3_fun(Ast, _z3.Z3_mk_label, [c_void_p, Symbol, c_int, Ast])

_z3_fun(Ast, _z3.Z3_mk_true, [c_void_p])
_z3_fun(Ast, _z3.Z3_mk_false, [c_void_p])
_z3_fun(Ast, _z3.Z3_mk_eq, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_distinct, [c_void_p, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_not, [c_void_p, Ast])
_z3_fun(Ast, _z3.Z3_mk_ite, [c_void_p, Ast, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_iff, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_implies, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_xor, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_and, [c_void_p, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_or, [c_void_p, c_uint, POINTER(Ast)])

_z3_fun(Ast, _z3.Z3_mk_add, [c_void_p, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_mul, [c_void_p, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_sub, [c_void_p, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_unary_minus, [c_void_p, Ast])
_z3_fun(Ast, _z3.Z3_mk_div, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_mod, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_rem, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_lt, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_le, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_gt, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_ge, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_int2real, [c_void_p, Ast])

_z3_fun(Ast, _z3.Z3_mk_bvnot, [c_void_p, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvand, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvor, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvxor, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvnand, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvnor, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvxnor, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvneg, [c_void_p, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvadd, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsub, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvmul, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvudiv, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsdiv, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvurem, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsrem, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsmod, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvult, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvslt, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvule, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsle, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvuge, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsge, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvugt, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsgt, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_concat, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_extract, [c_void_p, c_uint, c_uint, Ast])
_z3_fun(Ast, _z3.Z3_mk_sign_ext, [c_void_p, c_uint, Ast])
_z3_fun(Ast, _z3.Z3_mk_zero_ext, [c_void_p, c_uint, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvshl, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvlshr, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvashr, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_rotate_left, [c_void_p, c_uint, Ast])
_z3_fun(Ast, _z3.Z3_mk_rotate_right, [c_void_p, c_uint, Ast])
_z3_fun(Ast, _z3.Z3_mk_int2bv, [c_void_p, c_uint, Ast])
_z3_fun(Ast, _z3.Z3_mk_bv2int, [c_void_p, Ast, c_int])
_z3_fun(Ast, _z3.Z3_mk_bvadd_no_overflow, [c_void_p, Ast, Ast, c_int])
_z3_fun(Ast, _z3.Z3_mk_bvadd_no_underflow, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsub_no_overflow, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvsub_no_underflow, [c_void_p, Ast, Ast, c_int])
_z3_fun(Ast, _z3.Z3_mk_bvsdiv_no_overflow, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvneg_no_overflow, [c_void_p, Ast])
_z3_fun(Ast, _z3.Z3_mk_bvmul_no_overflow, [c_void_p, Ast, Ast, c_int])
_z3_fun(Ast, _z3.Z3_mk_bvmul_no_underflow, [c_void_p, Ast, Ast])

_z3_fun(Ast, _z3.Z3_mk_select, [c_void_p, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_store, [c_void_p, Ast, Ast, Ast])
_z3_fun(Ast, _z3.Z3_mk_const_array, [c_void_p, Sort, Ast])
_z3_fun(Ast, _z3.Z3_mk_map, [c_void_p, FuncDecl, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_array_default, [c_void_p, Ast])

_z3_fun(Ast, _z3.Z3_mk_numeral, [c_void_p, c_char_p, Sort])
_z3_fun(Ast, _z3.Z3_mk_real, [c_void_p, c_int, c_int])
_z3_fun(Ast, _z3.Z3_mk_int, [c_void_p, c_int, Sort])
_z3_fun(Ast, _z3.Z3_mk_unsigned_int, [c_void_p, c_uint, Sort])
_z3_fun(Ast, _z3.Z3_mk_int64, [c_void_p, c_longlong, Sort])
_z3_fun(Ast, _z3.Z3_mk_unsigned_int64, [c_void_p, c_ulonglong, Sort])

_z3_fun(Pattern, _z3.Z3_mk_pattern, [c_void_p, c_uint, POINTER(Ast)])
_z3_fun(Ast, _z3.Z3_mk_bound, [c_void_p, c_uint, Sort])
_z3_fun(Ast, _z3.Z3_mk_forall, [c_void_p, c_uint, c_uint, POINTER(Pattern),
  c_uint, POINTER(Sort), POINTER(Symbol), Ast])
_z3_fun(Ast, _z3.Z3_mk_exists, [c_void_p, c_uint, c_uint, POINTER(Pattern),
  c_uint, POINTER(Sort), POINTER(Symbol), Ast])
_z3_fun(Ast, _z3.Z3_mk_quantifier, [c_void_p, c_int, c_uint, c_uint,
  POINTER(Pattern), c_uint, POINTER(Sort), POINTER(Symbol), Ast])
_z3_fun(Ast, _z3.Z3_mk_forall_const, [c_void_p, c_uint, c_uint, POINTER(App),
  c_uint, POINTER(Pattern), Ast])
_z3_fun(Ast, _z3.Z3_mk_exists_const, [c_void_p, c_uint, c_uint, POINTER(App),
  c_uint, POINTER(Pattern), Ast])

_z3_fun(c_int, _z3.Z3_get_ast_kind, [c_void_p, Ast])
_z3_fun(Sort, _z3.Z3_get_sort, [c_void_p, Ast])

_z3_fun(c_char_p, _z3.Z3_get_numeral_string, [c_void_p, Ast])
_z3_fun(c_int, _z3.Z3_get_numeral_small, [c_void_p, Ast, POINTER(c_longlong),
  POINTER(c_longlong)])
_z3_fun(c_int, _z3.Z3_get_numeral_int, [c_void_p, Ast, POINTER(c_int)])
_z3_fun(c_int, _z3.Z3_get_numeral_uint, [c_void_p, Ast, POINTER(c_uint)])
_z3_fun(c_int, _z3.Z3_get_numeral_int64, [c_void_p, Ast, POINTER(c_longlong)])
_z3_fun(c_int, _z3.Z3_get_numeral_uint64, [c_void_p, Ast,
  POINTER(c_ulonglong)])
_z3_fun(c_int, _z3.Z3_get_bool_value, [c_void_p, Ast])

_z3_fun(FuncDecl, _z3.Z3_get_app_decl, [c_void_p, App])
_z3_fun(c_uint, _z3.Z3_get_app_num_args, [c_void_p, App])
_z3_fun(Ast, _z3.Z3_get_app_arg, [c_void_p, App, c_uint])
_z3_fun(Ast, _z3.Z3_app_to_ast, [c_void_p, App])
_z3_fun(App, _z3.Z3_to_app, [c_void_p, Ast])

_z3_fun(c_uint, _z3.Z3_get_index_value, [c_void_p, Ast])
_z3_fun(c_int, _z3.Z3_is_quantifier_forall, [c_void_p, Ast])
_z3_fun(c_uint, _z3.Z3_get_quantifier_weight, [c_void_p, Ast])
_z3_fun(c_uint, _z3.Z3_get_quantifier_num_patterns, [c_void_p, Ast])
_z3_fun(Pattern, _z3.Z3_get_quantifier_pattern_ast, [c_void_p, Ast, c_uint])
_z3_fun(c_uint, _z3.Z3_get_quantifier_num_bound, [c_void_p, Ast])
_z3_fun(Symbol, _z3.Z3_get_quantifier_bound_name, [c_void_p, Ast, c_uint])
_z3_fun(Sort, _z3.Z3_get_quantifier_bound_sort, [c_void_p, Ast, c_uint])
_z3_fun(Ast, _z3.Z3_get_quantifier_body, [c_void_p, Ast])
_z3_fun(c_uint, _z3.Z3_get_pattern_num_terms, [c_void_p, Pattern])
_z3_fun(Ast, _z3.Z3_get_pattern, [c_void_p, Pattern, c_uint])

_z3_fun(Ast, _z3.Z3_simplify, [c_void_p, Ast])

_z3_fun_void(_z3.Z3_push, [c_void_p])
_z3_fun_void(_z3.Z3_pop, [c_void_p, c_uint])
_z3_fun_void(_z3.Z3_persist_ast, [c_void_p, Ast, c_uint])
_z3_fun_void(_z3.Z3_assert_cnstr, [c_void_p, Ast])
_z3_fun(c_int, _z3.Z3_check, [c_void_p])
_z3_fun(c_int, _z3.Z3_check_and_get_model, [c_void_p, POINTER(Model)])
_z3_fun(c_int, _z3.Z3_check_assumptions, [c_void_p, c_uint, POINTER(Ast),
  POINTER(Model), POINTER(Ast), POINTER(c_uint), POINTER(Ast)])
_z3_fun_void(_z3.Z3_soft_check_cancel, [c_void_p])
_z3_fun(c_int, _z3.Z3_get_search_failure, [c_void_p])
_z3_fun_void(_z3.Z3_del_model, [c_void_p, Model])

_z3_fun(Literals, _z3.Z3_get_relevant_labels, [c_void_p])
_z3_fun(Literals, _z3.Z3_get_relevant_literals, [c_void_p])
_z3_fun(Literals, _z3.Z3_get_guessed_literals, [c_void_p])
_z3_fun_void(_z3.Z3_del_literals, [c_void_p, Literals])
_z3_fun(c_uint, _z3.Z3_get_num_literals, [c_void_p, Literals])
_z3_fun(Symbol, _z3.Z3_get_label_symbol, [c_void_p, Literals, c_uint])
_z3_fun(Ast, _z3.Z3_get_literal, [c_void_p, Literals, c_uint])
_z3_fun_void(_z3.Z3_disable_literal, [c_void_p, Literals, c_uint])
_z3_fun_void(_z3.Z3_block_literals, [c_void_p, Literals])

_z3_fun(c_uint, _z3.Z3_get_model_num_constants, [c_void_p, Model])
_z3_fun(FuncDecl, _z3.Z3_get_model_constant, [c_void_p, Model, c_uint])
_z3_fun(c_int, _z3.Z3_eval_func_decl, [c_void_p, Model, FuncDecl,
  POINTER(Ast)])
_z3_fun(c_uint, _z3.Z3_get_model_num_funcs, [c_void_p, Model])
_z3_fun(FuncDecl, _z3.Z3_get_model_func_decl, [c_void_p, Model, c_uint])
_z3_fun(c_uint, _z3.Z3_get_model_func_num_entries, [c_void_p, Model, c_uint])
_z3_fun(c_uint, _z3.Z3_get_model_func_entry_num_args, [c_void_p, Model, c_uint,
  c_uint])
_z3_fun(Ast, _z3.Z3_get_model_func_entry_arg, [c_void_p, Model, c_uint, c_uint,
  c_uint])
_z3_fun(Ast, _z3.Z3_get_model_func_entry_value, [c_void_p, Model, c_uint,
  c_uint])
_z3_fun(Ast, _z3.Z3_get_model_func_else, [c_void_p, Model, c_uint])
_z3_fun(c_int, _z3.Z3_is_array_value, [c_void_p, Ast, POINTER(c_uint)])
_z3_fun_void(_z3.Z3_get_array_value, [c_void_p, Ast, c_uint, POINTER(Ast),
  POINTER(Ast), POINTER(Ast)])
_z3_fun(c_int, _z3.Z3_eval, [c_void_p, Model, Ast, POINTER(Ast)])

_z3_fun_void(_z3.Z3_set_ast_print_mode, [c_void_p, c_uint])
_z3_fun(c_char_p, _z3.Z3_context_to_string, [c_void_p])
_z3_fun(c_char_p, _z3.Z3_sort_to_string, [c_void_p, Sort])
_z3_fun(c_char_p, _z3.Z3_func_decl_to_string, [c_void_p, FuncDecl])
_z3_fun(c_char_p, _z3.Z3_ast_to_string, [c_void_p, Ast])
_z3_fun(c_char_p, _z3.Z3_pattern_to_string, [c_void_p, Pattern])
_z3_fun(c_char_p, _z3.Z3_model_to_string, [c_void_p, Model])
_z3_fun(c_char_p, _z3.Z3_benchmark_to_smtlib_string, [c_void_p, c_char_p,
  c_char_p, c_char_p, c_char_p, c_uint, POINTER(Ast), Ast])
_z3_fun(Ast, _z3.Z3_get_context_assignment, [c_void_p])

_z3_fun_void(_z3.Z3_parse_smtlib_string, [c_void_p, c_char_p, c_uint,
  POINTER(Symbol), POINTER(Sort), c_uint, POINTER(Symbol), POINTER(FuncDecl)])
_z3_fun_void(_z3.Z3_parse_smtlib_file, [c_void_p, c_char_p, c_uint,
  POINTER(Symbol), POINTER(Sort), c_uint, POINTER(Symbol), POINTER(FuncDecl)])
_z3_fun(c_uint, _z3.Z3_get_smtlib_num_formulas, [c_void_p])
_z3_fun(Ast, _z3.Z3_get_smtlib_formula, [c_void_p, c_uint])
_z3_fun(c_uint, _z3.Z3_get_smtlib_num_assumptions, [c_void_p])
_z3_fun(Ast, _z3.Z3_get_smtlib_assumption, [c_void_p, c_uint])
_z3_fun(c_uint, _z3.Z3_get_smtlib_num_decls, [c_void_p])
_z3_fun(FuncDecl, _z3.Z3_get_smtlib_decl, [c_void_p, c_uint])

_z3_fun(Ast, _z3.Z3_parse_z3_string, [c_void_p, c_char_p])
_z3_fun(Ast, _z3.Z3_parse_z3_file, [c_void_p, c_char_p])

_z3_fun(Ast, _z3.Z3_parse_simplify_string, [c_void_p, c_char_p,
  POINTER(c_char_p)])
_z3_fun(Ast, _z3.Z3_parse_simplify_file, [c_void_p, c_char_p,
  POINTER(c_char_p)])

